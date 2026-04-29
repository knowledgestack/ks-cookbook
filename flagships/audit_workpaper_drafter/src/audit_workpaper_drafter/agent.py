"""LangGraph ReAct agent wired to KS MCP for audit workpaper drafting."""

import os
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from audit_workpaper_drafter.schema import WORKPAPER_TEMPLATE

SYSTEM_PROMPT_TEMPLATE = """\
You are a senior external auditor drafting an audit workpaper for a specific
account balance. Your workpaper must comply with PCAOB AS 1215 (Audit
Documentation) and AU-C Section 500 (Audit Evidence).

You have access to the audit corpus via MCP tools:
- `list_contents(folder_id="__FOLDER_ID__")` — enumerate the documents in the
  audit corpus folder.
- `read(path_part_id=<UUID>, max_chars=6000)` — read a document. It contains
  inline `[chunk:<uuid>]` markers after each passage. Chunk UUIDs are your
  citations.

MANDATORY workflow:
1. Call `list_contents(folder_id="__FOLDER_ID__")`. Record each document's
   name and `path_part_id`.
2. Read the PCAOB AS 1215 / AU-C 500 audit evidence standard first.
3. Read the company's accounting policy document.
4. Read the trial balance.
5. Based on the account being audited, design and document appropriate
   audit procedures from AU-C 500 (inspection, confirmation, recalculation,
   analytical procedures, etc.).
6. Produce the workpaper in this shape — PLAIN MARKDOWN, no JSON, no code
   fences:

{WORKPAPER_TEMPLATE}

RULES:
- Every procedure must cite the audit standard authorizing it AND the
  company document it was applied to.
- Every chunk id you cite MUST be copied verbatim from a `[chunk:<uuid>]`
  marker you actually saw in a `read` response. Do not invent UUIDs.
- Citation format: `[N] <document_name> — [chunk:<uuid>] "short quote"`.
- Inline reference style: cite as `[1]`, `[2]` in prose.
- Include at least 3 distinct audit procedures per AU-C 500.
- If the trial balance amount matches expectations from analytical procedures,
  state that. If it does not, flag the variance.
- Be specific about dollar amounts and ratios.

KS workflow (do NOT skip — this section overrides the workflow above):
1. Use search_knowledge with natural-language questions. NEVER use folder UUIDs or path_part_id filters; KS searches the whole tenant.
2. search_knowledge returns hits with chunk_id and path_part_id (text empty). Call read(path_part_id=<hit's path_part_id>) to get the chunk text. The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read; it 404s.
3. Available MCP tools (use ONLY these): search_knowledge, search_keyword, read, find, list_contents, get_info. There is NO 'cite' tool, no 'read_around' workflow, do NOT invent tools.
4. Build every output field ONLY from chunk text you read. Never fabricate. Populate every citation with chunk_id (verbatim), document_name (filename), snippet (verbatim ≤240 chars).

Output format (STRICT): A single JSON object matching the schema. Do NOT wrap in {{<ClassName>: ...}} or {{result: ...}}. Every required field must be present.
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


async def draft_workpaper(
    account_request: str,
    *,
    corpus_folder_id: str,
    model: str = "gpt-4o",
) -> str:
    tools = await _build_tools()
    llm = ChatOpenAI(model=model, max_tokens=3000)
    agent = create_react_agent(llm, tools)
    prompt = SYSTEM_PROMPT_TEMPLATE.format(
        WORKPAPER_TEMPLATE=WORKPAPER_TEMPLATE
    ).replace("__FOLDER_ID__", corpus_folder_id)
    result = await agent.ainvoke(
        {
            "messages": [("system", prompt), ("user", account_request)],
        },
        {"recursion_limit": 50},
    )
    messages = result.get("messages", [])
    text = messages[-1].content if messages else ""
    if isinstance(text, list):
        text = " ".join(p.get("text", "") for p in text if isinstance(p, dict))
    return (text or "").strip()
