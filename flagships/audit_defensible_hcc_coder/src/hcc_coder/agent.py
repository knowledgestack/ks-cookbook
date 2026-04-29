"""pydantic-ai agent that assigns HCC / ICD-10 codes grounded in a KS chart corpus."""

import os

from pydantic_ai import Agent
from pydantic_ai.usage import UsageLimits
from pydantic_ai.mcp import MCPServerStdio

from hcc_coder.schema import CoderReport

SYSTEM_TEMPLATE = """\
You are a certified HCC / ICD-10-CM coder producing an audit-defensible coding
report. Every code you emit must be tied to a specific clinical phrase in the
chart and a chunk UUID returned by the MCP server.

MANDATORY workflow:
1. Call ``search_knowledge`` (no folder_id; whole tenant) to find
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

KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs or path_part_id filters.
2. search_knowledge returns hits with chunk_id and path_part_id; the text field is empty by design. Call read(path_part_id=<hit's path_part_id>) to get chunk content. The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read; it 404s.
3. Build every output field ONLY from chunk text you read. Never fabricate.
4. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() metadata or materialized_path), snippet (verbatim ≤240 chars).

Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones.
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
        system_prompt=SYSTEM_TEMPLATE,
        output_type=CoderReport,
        retries=4,
        output_retries=4,
    )
    prompt = (
        f"Patient ID: {patient_id}. Read every chart document in the corpus and "
        "produce the full audit-defensible coder report."
    )
    async with agent.run_mcp_servers():
        result = await agent.run(prompt, usage_limits=UsageLimits(request_limit=200))
    return getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[return-value]
