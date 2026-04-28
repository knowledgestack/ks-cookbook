"""
LangGraph ReAct agent for drafting CIOMS adverse-event narratives
using Knowledge Stack MCP retrieval.
"""

from __future__ import annotations

import os
from typing import Any, List

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from adverse_event_narrative.schema import MEMO_TEMPLATE


# -------------------------------------------------------------------
# SYSTEM PROMPT
# -------------------------------------------------------------------

SYSTEM_PROMPT_TEMPLATE = """\
You are a pharmacovigilance specialist drafting a CIOMS-format
adverse-event narrative.

The drug label and PV SOP documents exist in the Knowledge Stack corpus.

You can access Knowledge Stack MCP tools:

TOOLS
-----
find(query=...)
    Locate likely documents anywhere in the tenant.

list_contents(folder_id=...)
    Enumerate documents inside a known corpus folder.

read(path_part_id=<UUID>, max_chars=6000)
    Read document text. Returns inline [chunk:<uuid>] markers.

MANDATORY WORKFLOW
------------------
1. __DISCOVERY_STEP__
2. Read the PV SOP document to understand causality assessment criteria.
3. Read the drug label for the specified drug.
4. Draft the narrative using the template below.

OUTPUT FORMAT
-------------
Plain Markdown only.
No JSON.
No code fences.

{MEMO_TEMPLATE}

CITATION RULES
--------------
• Every SOP or drug-label claim MUST cite a chunk marker.
• Use markers exactly as returned by read().
• Inline citation format:

    [N] <document_name> — [chunk:<uuid>] "short quote"

• Resolve citations in numbered list at bottom.
• If causality cannot be assessed:

    write "INSUFFICIENT DATA"
    and explain what is missing.

IMPORTANT
---------
Always reference documents using path_part_id values,
NOT filenames.
"""


# -------------------------------------------------------------------
# TOOL LOADING
# -------------------------------------------------------------------


async def _load_mcp_tools(include_list_contents: bool) -> List[Any]:
    """
    Initialize Knowledge Stack MCP tools.

    Uses env-configurable command so this works in:
    - local dev
    - docker
    - CI
    - uvx launcher
    """

    command = os.getenv("KS_MCP_COMMAND", "uvx")
    args = os.getenv("KS_MCP_ARGS", "knowledgestack-mcp").split()

    client = MultiServerMCPClient(
        {
            "knowledgestack": {
                "command": command,
                "args": args,
                "transport": "stdio",
                "env": {
                    "KS_API_KEY": os.getenv("KS_API_KEY", ""),
                    "KS_BASE_URL": os.getenv("KS_BASE_URL", ""),
                },
            }
        }
    )

    tools = await client.get_tools()

    if include_list_contents:
        return tools

    return [tool for tool in tools if getattr(tool, "name", "") != "list_contents"]


# -------------------------------------------------------------------
# PROMPT BUILDER
# -------------------------------------------------------------------


def _build_system_prompt(corpus_folder_id: str | None) -> str:
    """
    Inject discovery strategy depending on whether corpus folder exists.
    """

    if corpus_folder_id:
        discovery_step = (
            f'Call list_contents(folder_id="{corpus_folder_id}") '
            "and record each document name and path_part_id."
        )

    else:
        discovery_step = (
            "Do NOT call list_contents. Use find() to locate the PV SOP and drug label."
        )

    return SYSTEM_PROMPT_TEMPLATE.replace(
        "__DISCOVERY_STEP__",
        discovery_step,
    ).format(MEMO_TEMPLATE=MEMO_TEMPLATE)


# -------------------------------------------------------------------
# AGENT ENTRYPOINT
# -------------------------------------------------------------------


async def draft_narrative(
    *,
    event: str,
    drug: str,
    corpus_folder_id: str | None = None,
    model: str = "gpt-4o",
) -> str:
    """
    Draft CIOMS adverse-event narrative using Knowledge Stack MCP retrieval.
    """

    tools = await _load_mcp_tools(include_list_contents=bool(corpus_folder_id))

    llm = ChatOpenAI(
        model=model,
        temperature=0,
        max_tokens=3000,
    )

    agent = create_react_agent(llm, tools)

    system_prompt = _build_system_prompt(corpus_folder_id)

    user_prompt = (
        f"Drug: {drug}\n"
        f"Adverse event description: {event}\n\n"
        "Draft the CIOMS narrative now."
    )

    result = await agent.ainvoke(
        {
            "messages": [
                ("system", system_prompt),
                ("user", user_prompt),
            ]
        },
        {"recursion_limit": 50},
    )

    messages = result.get("messages", [])

    if not messages:
        return ""

    output = messages[-1].content

    if isinstance(output, list):
        output = " ".join(
            part.get("text", "") for part in output if isinstance(part, dict)
        )

    return (output or "").strip()
