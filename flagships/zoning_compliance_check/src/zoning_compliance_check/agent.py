"""LangGraph ReAct agent wired to KS MCP for zoning compliance checks."""


import os
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from zoning_compliance_check.schema import COMPLIANCE_TEMPLATE

SYSTEM_PROMPT_TEMPLATE = """\
You are a municipal zoning analyst checking whether a proposed use at a
given address complies with the City of Austin Land Development Code
(Chapter 25-2).

You have access to the Austin zoning code corpus via MCP tools:
- `find(query=...)` locates likely zoning-code documents by title anywhere in the tenant.
- `list_contents` on a folder id returns the documents it contains when a corpus folder is provided.
- `read(path_part_id=<UUID>, max_chars=6000)` returns the document text with
  inline `[chunk:<uuid>]` markers after each passage. Chunk UUIDs are your
  citations.

MANDATORY workflow:
1. __DISCOVERY_STEP__
2. Read the `austin_ldc_zoning_districts` to identify the zone district and
   its development standards.
3. Read the `austin_ldc_permitted_uses_table` to determine if the proposed
   use is Permitted (P), Conditional (C), or Not Permitted (--) in the
   zone district.
4. If the use is Conditional, read `austin_ldc_conditional_use` for CUP
   requirements and compatibility standards.
5. Produce the compliance report in PLAIN MARKDOWN following this shape:

{COMPLIANCE_TEMPLATE}

RULES:
- Determine permitted status: YES (P in table), CONDITIONAL (C in table),
  NO (-- in table), or VARIANCE_REQUIRED (use variance not available in TX,
  so applicant must rezone).
- Every factual claim MUST be backed by a citation from the corpus.
- Every chunk id you cite MUST be copied verbatim from a `[chunk:<uuid>]`
  marker you actually saw in a `read` response. Do not invent UUIDs.
- Citation format: `[N] document_name -- [chunk:<uuid>] "short quote"`.
- Be specific about which LDC section applies.

ADDRESS: {address}
ZONE DISTRICT: {zone_district}
PROPOSED USE: {proposed_use}
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


async def check_zoning(
    *,
    address: str,
    zone_district: str,
    proposed_use: str,
    corpus_folder_id: str | None,
    model: str = "gpt-4o",
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
            "Do NOT call `list_contents`. Use `find` to locate the Austin LDC "
            "zoning district, permitted uses, and conditional use documents by "
            "title keywords such as `austin`, `ldc`, `zoning`, `permitted`, "
            "and `conditional`."
        )
    prompt = SYSTEM_PROMPT_TEMPLATE.format(
        COMPLIANCE_TEMPLATE=COMPLIANCE_TEMPLATE,
        address=address,
        zone_district=zone_district,
        proposed_use=proposed_use,
    ).replace("__DISCOVERY_STEP__", discovery_step)
    result = await agent.ainvoke(
        {
            "messages": [
                ("system", prompt),
                (
                    "user",
                    f"Check zoning compliance for a '{proposed_use}' at "
                    f"{address} (zoned {zone_district}).",
                ),
            ],
        },
        {"recursion_limit": 50},
    )
    messages = result.get("messages", [])
    text = messages[-1].content if messages else ""
    if isinstance(text, list):
        text = " ".join(
            p.get("text", "") for p in text if isinstance(p, dict)
        )
    return (text or "").strip()
