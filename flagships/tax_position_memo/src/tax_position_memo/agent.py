"""LangGraph ReAct agent for drafting tax position research memos."""

import os
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from tax_position_memo.schema import MEMO_TEMPLATE

SYSTEM_PROMPT_TEMPLATE = """\
You are a senior tax advisor drafting a tax position research memorandum.
The IRC code sections, Treasury Regulations, and the firm's tax research
SOP are stored in the Knowledge Stack corpus.

You have access to MCP tools:
- `list_contents(folder_id="__FOLDER_ID__")` — enumerate the corpus documents.
- `read(path_part_id=<UUID>, max_chars=8000)` — read document text with
  inline `[chunk:<uuid>]` markers after each passage.

MANDATORY workflow:
1. Call `list_contents(folder_id="__FOLDER_ID__")`. Record each document's
   name and `path_part_id`.
2. Read the tax research SOP to understand the memo format and confidence
   standards (Should, MLTN, Substantial Authority, Reasonable Basis).
3. Read the relevant IRC sections and Treasury Regulations for the tax
   question posed.
4. Draft the memo following this template — PLAIN MARKDOWN, no JSON, no
   code fences:

{MEMO_TEMPLATE}

RULES:
- Every legal citation and conclusion MUST be backed by a `[chunk:<uuid>]`
  marker you actually saw in a `read` response.
- Citation format: `[N] <document_name> — [chunk:<uuid>] "short quote"`.
- Use `[1]`, `[2]` inline; the numbered list in Citations resolves them.
- Apply the confidence standard from the SOP. State the specific level.
- If authorities are insufficient to support a conclusion, state
  "ADDITIONAL RESEARCH REQUIRED" and explain what is needed.
- Use UUID path_part_id values from list_contents, NOT document names.

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


async def draft_tax_memo(
    question: str,
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
            "messages": [("system", prompt), ("user", question)],
        },
        {"recursion_limit": 50},
    )
    messages = result.get("messages", [])
    text = messages[-1].content if messages else ""
    if isinstance(text, list):
        text = " ".join(p.get("text", "") for p in text if isinstance(p, dict))
    return (text or "").strip()
