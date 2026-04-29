"""pydantic-ai agent that drafts a denial rebuttal grounded in chart + payer policy."""

import os

from pydantic_ai import Agent
from pydantic_ai.usage import UsageLimits
from pydantic_ai.mcp import MCPServerStdio

from claims_rebuttal.schema import RebuttalLetter

SYSTEM_TEMPLATE = """\
You are a utilization-review nurse drafting an appeal letter for a payer
denial. Every coverage criterion must cite the payer policy by chunk UUID,
and every supporting evidence snippet must cite the patient chart by chunk
UUID. No ungrounded claims.

MANDATORY workflow:
1. Call ``list_contents`` with ``folder_id=__CHART_FOLDER_ID__`` to enumerate
   the patient chart documents.
2. Call ``list_contents`` with ``folder_id=__POLICY_FOLDER_ID__`` to enumerate
   payer policy documents.
3. Use ``search_keyword`` on the policy corpus for the denial code
   ``__DENIAL_CODE__`` and for the service in question to locate the governing
   coverage criteria.
4. Use ``search_knowledge`` on the chart corpus for each criterion (e.g.
   "prior conservative therapy", "failed first-line medication") — then call
   ``read_around`` on the top hits so the supporting snippet carries enough
   surrounding clinical context to stand alone in the letter.
5. Every ``Citation.chunk_id`` MUST be copied verbatim from a
   ``[chunk:<uuid>]`` marker in MCP output.
6. For each criterion, set ``is_met`` only if the chart citations clearly
   document it. If a criterion is NOT met, still include it and state that
   the appeal is based on the other criteria or medical necessity exception.
7. The letter must be payer-ready — formal tone, no hedging language, no
   speculation.

KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs or path_part_id filters.
2. search_knowledge returns hits with chunk_id and path_part_id; the text field is empty by design. Call read(path_part_id=<hit's path_part_id>) to get chunk content. The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read; it 404s.
3. Build every output field ONLY from chunk text you read. Never fabricate.
4. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() metadata or materialized_path), snippet (verbatim ≤240 chars).

Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones.
"""


async def draft_rebuttal(
    *,
    patient_id: str,
    denial_code: str,
    payer: str,
    service: str,
    chart_folder_id: str,
    policy_folder_id: str,
    model: str,
) -> RebuttalLetter:
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
    system = (
        SYSTEM_TEMPLATE.replace("__CHART_FOLDER_ID__", chart_folder_id)
        .replace("__POLICY_FOLDER_ID__", policy_folder_id)
        .replace("__DENIAL_CODE__", denial_code)
    )
    agent = Agent(
        model=f"openai:{model}",
        mcp_servers=[mcp],
        system_prompt=system,
        output_type=RebuttalLetter,
        retries=4,
        output_retries=4,
    )
    prompt = (
        f"Patient: {patient_id}. Denial code: {denial_code}. Payer: {payer}. "
        f"Service in question: {service}. Draft the full appeal letter."
    )
    async with agent.run_mcp_servers():
        result = await agent.run(prompt, usage_limits=UsageLimits(request_limit=200))
    return getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[return-value]
