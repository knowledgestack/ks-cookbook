"""LangGraph ReAct agent wired to KS MCP for coverage-analysis memos."""

import os
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from claim_adjudication_memo.schema import MEMO_TEMPLATE

SYSTEM_PROMPT_TEMPLATE = """\
You are a P&C claims adjudicator drafting a coverage-analysis memorandum.

You have access to the Acme Insurance claims corpus via MCP tools:
- `list_contents` on a folder id returns the documents it contains.
- `read(path_part_id=<UUID>, max_chars=6000)` returns the document text with
  inline `[chunk:<uuid>]` markers after each passage. Chunk UUIDs are your
  citations.

MANDATORY workflow:
1. Call `list_contents(path_part_id="__FOLDER_ID__")`. Record each document's
   name and `path_part_id`.
2. Always read the `claims_adjudication_sop` first so the memo follows the
   required checks.
3. Based on the loss narrative, read the applicable policy form:
   - First-party property loss (fire, wind, water, theft) → the HO-3 or
     similar homeowners/property form.
   - Third-party liability loss (bodily injury, property damage caused by
     insured, product liability) → the CGL form.
4. Produce the memo in this shape — PLAIN MARKDOWN, no JSON, no code fences:

{MEMO_TEMPLATE}

RULES:
- Every non-trivial factual claim in sections 2-7 MUST be backed by a
  citation entry at the bottom of the memo.
- Every chunk id you cite MUST be copied verbatim from a `[chunk:<uuid>]`
  marker you actually saw in a `read` response. Do not invent UUIDs.
- Citation format: `[N] <document_name> — [chunk:<uuid>] "short quote"`.
- Inline reference style: cite as `[1]`, `[2]` in prose; the numbered list at
  the bottom defines what each number resolves to.
- If a required SOP check cannot be answered from the policy text, write
  "INSUFFICIENT POLICY EVIDENCE" for that section and cite nothing.
- Be concise. The adjuster reads hundreds of these — bullet points fine.
"""


async def _build_tools() -> list[Any]:
    command = os.environ.get("KS_MCP_COMMAND", "uvx")
    args_raw = os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp")
    args = args_raw.split() if args_raw else []
    client = MultiServerMCPClient(
        {
            "knowledgestack": {
                "command": command,
                "args": args,
                "transport": "stdio",
                "env": {
                    "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
                    "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
                },
            }
        }
    )
    return await client.get_tools()


async def draft_memo(
    claim_narrative: str,
    *,
    corpus_folder_id: str,
    model: str = "gpt-4o",
) -> str:
    tools = await _build_tools()
    llm = ChatOpenAI(model=model, max_tokens=3000)
    agent = create_react_agent(llm, tools)
    prompt = SYSTEM_PROMPT_TEMPLATE.format(MEMO_TEMPLATE=MEMO_TEMPLATE).replace(
        "__FOLDER_ID__", corpus_folder_id
    )
    result = await agent.ainvoke(
        {
            "messages": [("system", prompt), ("user", claim_narrative)],
        },
        {"recursion_limit": 50},
    )
    messages = result.get("messages", [])
    text = messages[-1].content if messages else ""
    if isinstance(text, list):
        text = " ".join(p.get("text", "") for p in text if isinstance(p, dict))
    return (text or "").strip()
