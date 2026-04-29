"""LangGraph ReAct agent wired to KS MCP for covenant compliance monitoring."""

import os
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from loan_covenant_monitor.schema import REPORT_TEMPLATE

SYSTEM_PROMPT_TEMPLATE = """\
You are a credit risk analyst monitoring loan covenant compliance. Your job is
to read the credit agreement and the borrower's quarterly financial report,
then produce a covenant compliance report comparing each financial covenant
against the actual reported figures.

You have access to the borrower's corpus via MCP tools:
- `find(query=...)` — locate likely documents by title anywhere in the tenant.
- `list_contents(folder_id="__FOLDER_ID__")` — enumerate the documents when a corpus folder is provided.
- `read(path_part_id=<UUID>, max_chars=8000)` — read document text with inline
  `[chunk:<uuid>]` markers after each passage.

MANDATORY workflow:
1. __DISCOVERY_STEP__
2. Read the **credit agreement** document first. Extract ALL financial covenants:
   - Maximum Consolidated Leverage Ratio (with step-down schedule)
   - Minimum Consolidated Interest Coverage Ratio (with step-down schedule)
   - Minimum Consolidated Fixed Charge Coverage Ratio
   - Minimum Consolidated Tangible Net Worth
   - Also note cure rights and events of default.
3. Read the **quarterly financial report**. Extract the actual figures:
   - Consolidated Total Debt, Consolidated EBITDA, Interest Expense
   - The borrower's own covenant compliance summary if present
   - Tangible Net Worth calculation
4. For EACH covenant, compare the required threshold (for the applicable test
   period) against the actual value. Determine status:
   - COMPLIANT: actual meets or exceeds the threshold with comfortable headroom
   - WARNING: actual meets the threshold but headroom is less than 20% of the
     threshold value, OR the borrower flags a concern
   - BREACH: actual fails to meet the threshold
5. Produce the report in PLAIN MARKDOWN (no JSON, no code fences) using this
   structure:

{REPORT_TEMPLATE}

RULES:
- Every factual claim MUST be backed by a citation at the bottom.
- Every chunk id you cite MUST be copied verbatim from a `[chunk:<uuid>]`
  marker you actually saw in a `read` response. Do NOT invent UUIDs.
- Citation format: `[N] <document_name> — [chunk:<uuid>] "short quote"`.
- Inline reference: cite as `[1]`, `[2]` in prose.
- For the Recommended Actions section: if any covenant is in BREACH, recommend
  specific cure options (equity cure, asset sale, covenant amendment request).
  If WARNING, recommend monitoring frequency increase. If all COMPLIANT,
  note the covenant with the thinnest headroom.
- Be quantitatively precise. Show calculations.

KS workflow (do NOT skip — this section overrides the workflow above):
1. Use search_knowledge with natural-language questions. NEVER use folder UUIDs or path_part_id filters; KS searches the whole tenant.
2. search_knowledge returns hits with chunk_id and path_part_id (text empty). Call read(path_part_id=<hit's path_part_id>) to get the chunk text. The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read; it 404s.
3. Available MCP tools (use ONLY these): search_knowledge, search_keyword, read, find, list_contents, get_info. There is NO 'cite' tool, no 'read_around' workflow, do NOT invent tools.
4. Build every output field ONLY from chunk text you read. Never fabricate. Populate every citation with chunk_id (verbatim), document_name (filename), snippet (verbatim ≤240 chars).

Output format (STRICT): A single JSON object matching the schema. Do NOT wrap in {{<ClassName>: ...}} or {{result: ...}}. Every required field must be present.
"""


async def _build_tools(*, include_list_contents: bool = True) -> list[Any]:
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
    tools = await client.get_tools()
    if include_list_contents:
        return tools
    return [tool for tool in tools if getattr(tool, "name", "") != "list_contents"]


async def monitor_covenants(
    *,
    borrower: str,
    period: str,
    corpus_folder_id: str | None,
    model: str = "gpt-4o",
) -> str:
    """Run the covenant monitoring agent; returns a Markdown report string."""
    tools = await _build_tools(include_list_contents=bool(corpus_folder_id))
    llm = ChatOpenAI(model=model, max_tokens=4000)
    agent = create_react_agent(llm, tools)
    if corpus_folder_id:
        discovery_step = (
            f'Call `list_contents(folder_id="{corpus_folder_id}")`. Record each '
            "document's name and `path_part_id`."
        )
    else:
        discovery_step = (
            "Do NOT call `list_contents`. Use `find` to locate the credit "
            "agreement and quarterly financial statements for the borrower by "
            "title keywords such as the borrower name, `credit agreement`, "
            "`quarterly`, and `financial`."
        )
    prompt = SYSTEM_PROMPT_TEMPLATE.format(
        REPORT_TEMPLATE=REPORT_TEMPLATE,
    ).replace("__DISCOVERY_STEP__", discovery_step)

    user_msg = (
        f"Analyze covenant compliance for {borrower} for the period {period}. "
        f"Read the credit agreement and quarterly financials, compare each "
        f"covenant to actuals, and produce the full compliance report."
    )

    result = await agent.ainvoke(
        {"messages": [("system", prompt), ("user", user_msg)]},
        {"recursion_limit": 50},
    )
    messages = result.get("messages", [])
    text = messages[-1].content if messages else ""
    if isinstance(text, list):
        text = " ".join(p.get("text", "") for p in text if isinstance(p, dict))
    return (text or "").strip()
