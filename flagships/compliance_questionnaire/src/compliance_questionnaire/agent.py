"""LangGraph agent that answers compliance questions, grounded in KS policies."""


import json
import os
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

SYSTEM_PROMPT_TEMPLATE = """\
You are an AI auditor filling out a security / compliance questionnaire (CAIQ /
SIG format) on behalf of a company. Ground every answer in the company's
policies, which are available in a Knowledge Stack tenant via MCP tools.

MANDATORY workflow per question:
1. Call `list_contents` on the POLICIES_FOLDER_ID provided below to see available
   policies. The response gives each policy's `path_part_id` (a UUID) and `name`.
2. Pick the 1-3 policies whose names best match the question (e.g. "access" for
   authentication questions, "ir" for incident response, "data_protection" for
   encryption, etc.).
3. For each relevant policy, call `read(path_part_id=<UUID copied verbatim from
   list_contents response>, max_chars=4000)`. DO NOT pass the policy name as
   path_part_id — it MUST be the UUID from the previous step.
   The response contains inline `[chunk:<uuid>]` markers after each passage.
4. Produce a JSON object (NO other text, NO markdown fences) with this exact shape:

   {
     "answer": "Yes | No | N/A | Partial | INSUFFICIENT EVIDENCE",
     "description": "Short auditor-style prose (1-3 sentences).",
     "confidence": "HIGH | MEDIUM | LOW",
     "citations": [
       {"chunk_id": "<uuid from [chunk:...] marker>",
        "document_name": "<policy name e.g. access>",
        "snippet": "<short quote from the chunk, <=400 chars>"}
     ]
   }

RULES:
- Every HIGH/MEDIUM answer MUST include at least one citation with a real chunk_id
  copied verbatim from the policy text.
- If retrieved policies do not support the question, answer
  "INSUFFICIENT EVIDENCE" with confidence=LOW and citations=[].
- Never invent chunk_ids or document names. Never quote text you didn't read.
- Be concise. Auditors read hundreds of these; no marketing prose.

POLICIES_FOLDER_ID: __FOLDER_ID__
"""


async def _build_tools() -> list[Any]:
    command = os.environ.get("KS_MCP_COMMAND", "uvx")
    args_raw = os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp")
    args = args_raw.split() if args_raw else []
    client = MultiServerMCPClient({
        "knowledgestack": {
            "command": command,
            "args": args,
            "transport": "stdio",
            "env": {
                "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
                "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
            },
        }
    })
    return await client.get_tools()


def _build_model() -> Any:
    provider = os.environ.get("COMPLIANCE_PROVIDER", "openai").lower()
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=os.environ.get("COMPLIANCE_MODEL", "claude-opus-4-6"),
            max_tokens=1500,
        )
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=os.environ.get("COMPLIANCE_MODEL", "gpt-4o"),
        max_tokens=1500,
    )


def _parse_json_reply(text: str) -> dict[str, Any]:
    """LLMs wrap JSON in varied ways — markdown fences, code blocks, prose. Be liberal."""
    import re

    cleaned = text.strip()
    # Strip markdown fences of any fence language.
    fence = re.match(r"^```[a-zA-Z]*\s*\n?(.*?)\n?```\s*$", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1).strip()

    # Try direct parse first.
    try:
        obj = json.loads(cleaned)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass

    # Fallback: find the largest balanced {...} substring.
    start = cleaned.find("{")
    if start < 0:
        raise ValueError(f"no JSON object in reply: {cleaned[:200]!r}")
    depth = 0
    for i in range(start, len(cleaned)):
        if cleaned[i] == "{":
            depth += 1
        elif cleaned[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    obj = json.loads(cleaned[start : i + 1])
                    if isinstance(obj, dict):
                        return obj
                except json.JSONDecodeError:
                    continue
    raise ValueError(f"unparseable reply: {cleaned[:200]!r}")


async def answer_one(
    *, control_id: str, question: str, policies_folder_id: str, tools: list[Any], model: Any,
) -> dict[str, Any]:
    prompt = SYSTEM_PROMPT_TEMPLATE.replace("__FOLDER_ID__", policies_folder_id)
    agent = create_react_agent(model, tools)
    result = await agent.ainvoke({
        "messages": [
            ("system", prompt),
            ("user", f"Control {control_id}: {question}"),
        ]
    })
    messages = result.get("messages", [])
    text = messages[-1].content if messages else ""
    if isinstance(text, list):
        text = " ".join(p.get("text", "") for p in text if isinstance(p, dict))
    return _parse_json_reply(text)
