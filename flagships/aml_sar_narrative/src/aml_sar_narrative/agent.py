"""pydantic-ai agent that drafts a SAR narrative grounded in KS-seeded case evidence."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from aml_sar_narrative.schema import SARNarrative

SYSTEM_TEMPLATE = """\
You are an AML investigator at a US bank. Draft a Suspicious Activity Report
narrative in FinCEN's Who / What / When / Where / Why / How format for the
case below, grounded strictly in the case evidence available under the
CORPUS folder via MCP tools (transaction ledger exports, alert rationale
memo, KYC file, prior SAR history, relevant FFIEC / FinCEN guidance).

MANDATORY workflow:
1. Call ``list_contents`` with ``folder_id=__CORPUS_FOLDER_ID__`` to enumerate
   the case file.
2. Call ``read`` on EACH relevant document using the UUID ``path_part_id``.
3. Every ``Citation.chunk_id`` you emit MUST be copied verbatim from a
   ``[chunk:<uuid>]`` marker in the ``read`` output.
4. Produce the structured ``SARNarrative``:
   - Keep ``narrative`` ≤ ~200 words; FinCEN format, flowing prose.
   - ``red_flags`` must be concrete behaviors (structuring, rapid pass-through,
     geographic risk, third-party funder inconsistency, etc.) — not generic
     phrases.
   - Do not speculate beyond what documents support. If a fact is absent,
     omit the red flag rather than inventing it.
"""


async def draft_sar(
    *,
    case_id: str,
    subject_hint: str,
    corpus_folder_id: str,
    model: str,
) -> SARNarrative:
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
        output_type=SARNarrative,
    )
    prompt = (
        f"Case ID: {case_id}. Subject (if known): {subject_hint or 'unknown'}. "
        "Read the case file and draft the SAR narrative."
    )
    async with agent.run_mcp_servers():
        result = await agent.run(prompt)
    return getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[return-value]
