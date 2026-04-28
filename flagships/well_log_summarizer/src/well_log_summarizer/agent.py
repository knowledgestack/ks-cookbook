"""pydantic-ai agent that summarizes well logs + drilling reports grounded in KS corpus."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from well_log_summarizer.schema import WellSummary

SYSTEM_TEMPLATE = """\
You are a drilling-operations engineer. Produce a cited summary for the well
below, grounded strictly in the documents available under the CORPUS folder
via MCP tools (DOE OpenEnergy filings, SPE papers, state RRC reports, operator
daily drilling reports).

MANDATORY workflow:
1. Call ``list_contents`` with ``folder_id=__CORPUS_FOLDER_ID__`` to enumerate
   available documents for the well.
2. Call ``read`` on each relevant document using its UUID ``path_part_id``.
3. Every ``Citation.chunk_id`` you emit MUST be copied verbatim from a
   ``[chunk:<uuid>]`` marker in the ``read`` output. Do not synthesize.
4. Produce the structured ``WellSummary``:
   - Classify each notable occurrence as hse / equipment / formation /
     lost_time / other with an evidenced severity.
   - ``hse_risk_rating`` must reflect the worst HSE event, not an average.
   - ``recommended_actions`` must be specific and actionable, not generic
     boilerplate.

Do not fabricate API numbers, depths, or formation names. If a value is
missing from the corpus, say so explicitly in ``depth_summary`` or
``formation_notes``.
"""


async def summarize_well(
    *,
    well_id: str,
    corpus_folder_id: str,
    model: str,
) -> WellSummary:
    server_cmd = os.environ.get("KS_MCP_COMMAND", "uvx")
    server_args = (os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split()
    mcp = MCPServerStdio(
        command=server_cmd,
        args=server_args,
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    agent = Agent(
        model=f"openai:{model}",
        mcp_servers=[mcp],
        system_prompt=SYSTEM_TEMPLATE.replace("__CORPUS_FOLDER_ID__", corpus_folder_id),
        output_type=WellSummary,
    )
    prompt = (
        f"Well ID: {well_id}. Read every relevant document in the corpus and "
        "produce the full structured summary."
    )
    async with agent.run_mcp_servers():
        result = await agent.run(prompt)
    return getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[return-value]
