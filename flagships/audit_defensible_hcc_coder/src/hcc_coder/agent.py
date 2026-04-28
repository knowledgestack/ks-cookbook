"""pydantic-ai agent that assigns HCC / ICD-10 codes grounded in a KS chart corpus."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from hcc_coder.schema import CoderReport

SYSTEM_TEMPLATE = """\
You are a certified HCC / ICD-10-CM coder producing an audit-defensible coding
report. Every code you emit must be tied to a specific clinical phrase in the
chart and a chunk UUID returned by the MCP server.

MANDATORY workflow:
1. Call ``list_contents`` with ``folder_id=__CORPUS_FOLDER_ID__`` to enumerate
   the chart documents (progress notes, problem list, labs, imaging).
2. Call ``read`` on every relevant document using its UUID ``path_part_id``.
   Do NOT invent UUIDs.
3. The ``read`` output contains ``[chunk:<uuid>]`` markers. Every
   ``Citation.chunk_id`` MUST be copied verbatim from one of those markers.
4. For each code in the ``CoderReport``:
   - Record the ``supporting_phrase`` EXACTLY as it appears in the chart.
   - Fill ``hcc_category`` only when the ICD-10 code maps to CMS-HCC v24/v28;
     otherwise leave it null.
   - ``confidence`` is ``high`` only when the clinical phrase + date of service
     are both explicit; ``medium`` when inferred; ``low`` should rarely appear.
5. If a patient carries a historical problem-list diagnosis with no current
   documentation in the corpus, add an ``unsupported_flags`` entry rather than
   coding it. M.E.A.T. (Monitor / Evaluate / Assess / Treat) is required.

Do not fabricate dates, labs, or findings.
"""


async def code_chart(
    *,
    patient_id: str,
    corpus_folder_id: str,
    model: str,
) -> CoderReport:
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
        output_type=CoderReport,
    )
    prompt = (
        f"Patient ID: {patient_id}. Read every chart document in the corpus and "
        "produce the full audit-defensible coder report."
    )
    async with agent.run_mcp_servers():
        result = await agent.run(prompt)
    return getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[return-value]
