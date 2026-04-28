"""pydantic-ai agent that drafts a denial rebuttal grounded in chart + payer policy."""

import os

from pydantic_ai import Agent
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
    )
    prompt = (
        f"Patient: {patient_id}. Denial code: {denial_code}. Payer: {payer}. "
        f"Service in question: {service}. Draft the full appeal letter."
    )
    async with agent.run_mcp_servers():
        result = await agent.run(prompt)
    return getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[return-value]
