"""pydantic-ai agent that summarizes well logs + drilling reports grounded in KS corpus."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.usage import UsageLimits

from well_log_summarizer.schema import WellSummary

SYSTEM_TEMPLATE = """\
You are a drilling-operations engineer. Produce a cited summary for the well
below, grounded strictly in the documents available under the CORPUS folder
via MCP tools (DOE OpenEnergy filings, SPE papers, state RRC reports, operator
daily drilling reports).

MANDATORY workflow:
1. Call ``search_knowledge`` (no folder_id; whole tenant) to find
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

KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs or path_part_id filters.
2. search_knowledge returns hits with chunk_id and path_part_id; the text field is empty by design. Call read(path_part_id=<hit's path_part_id>) to get chunk content. The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read; it 404s.
3. Build every output field ONLY from chunk text you read. Never fabricate.
4. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() metadata or materialized_path), snippet (verbatim ≤240 chars).

Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones.
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
        system_prompt=SYSTEM_TEMPLATE,
        output_type=WellSummary,
        retries=4,
        output_retries=4,
    )
    prompt = (
        f"Well ID: {well_id}. Read every relevant document in the corpus and "
        "produce the full structured summary."
    )
    async with agent.run_mcp_servers():
        result = await agent.run(prompt, usage_limits=UsageLimits(request_limit=200))
    return getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[return-value]
