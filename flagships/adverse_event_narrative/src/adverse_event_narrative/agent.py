"""LangGraph ReAct agent for drafting CIOMS adverse-event narratives."""


import os
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from adverse_event_narrative.schema import MEMO_TEMPLATE

SYSTEM_PROMPT_TEMPLATE = """\
You are a pharmacovigilance specialist drafting a CIOMS-format adverse event
narrative. The drug label and PV SOP documents are in the Knowledge Stack
corpus.

You have access to MCP tools:
- `find(query=...)` — locate likely documents by title anywhere in the tenant.
- `list_contents(folder_id=...)` — enumerate a known corpus folder when one is provided.
- `read(path_part_id=<UUID>, max_chars=6000)` — read document text with
  inline `[chunk:<uuid>]` markers after each passage.

MANDATORY workflow:
1. __DISCOVERY_STEP__
2. Read the PV SOP document to understand causality assessment criteria.
3. Read the drug label for the specified drug to get prescribing info,
   known adverse reactions, and contraindications.
4. Using the event description provided by the user, draft the narrative
   following this template — PLAIN MARKDOWN, no JSON, no code fences:

{MEMO_TEMPLATE}

RULES:
- Every factual claim about the drug or SOP procedure MUST cite a
  `[chunk:<uuid>]` marker you actually saw in a `read` response.
- Citation format: `[N] <document_name> — [chunk:<uuid>] "short quote"`.
- Use `[1]`, `[2]` inline; the numbered list at the bottom resolves them.
- If causality cannot be fully assessed from available info, state
  "INSUFFICIENT DATA" and explain what is missing.
- Use UUID path_part_id values from list_contents, NOT document names.
"""


async def _build_tools(*, include_list_contents: bool = True) -> list[Any]:
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
    tools = await client.get_tools()
    if include_list_contents:
        return tools
    return [tool for tool in tools if getattr(tool, "name", "") != "list_contents"]


async def draft_narrative(
    event: str, drug: str, *, corpus_folder_id: str | None, model: str = "gpt-4o",
) -> str:
    tools = await _build_tools(include_list_contents=bool(corpus_folder_id))
    llm = ChatOpenAI(model=model, max_tokens=3000)
    agent = create_react_agent(llm, tools)
    if corpus_folder_id:
        discovery_step = (
            f'Call `list_contents(folder_id="{corpus_folder_id}")`. Record each '
            "document's name and `path_part_id`."
        )
    else:
        discovery_step = (
            "Do NOT call `list_contents`. Use `find` to locate the PV SOP and "
            "the relevant drug label by title keywords such as `pv`, `sop`, "
            "`label`, and the drug name."
        )
    prompt = (
        SYSTEM_PROMPT_TEMPLATE.format(MEMO_TEMPLATE=MEMO_TEMPLATE)
        .replace("__DISCOVERY_STEP__", discovery_step)
    )
    user_msg = (
        f"Drug: {drug}\n"
        f"Adverse event description: {event}\n\n"
        f"Draft the CIOMS narrative now."
    )
    result = await agent.ainvoke({
        "messages": [("system", prompt), ("user", user_msg)],
    }, {"recursion_limit": 50})
    messages = result.get("messages", [])
    text = messages[-1].content if messages else ""
    if isinstance(text, list):
        text = " ".join(p.get("text", "") for p in text if isinstance(p, dict))
    return (text or "").strip()
