"""pydantic-ai agent that turns a SOAP note into 3 cited artifacts."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.usage import UsageLimits

from chiro_autopilot.schema import VisitAutopilotOutput

SYSTEM_TEMPLATE = """\
You are the operations AI for a chiropractic clinic running on ChiroCRM by
DB Streams. From the patient's most recent SOAP note, produce three
deliverables IN ONE STRUCTURED OUTPUT:

  A) ``codes`` — the billable CPT / ICD-10 / HCPCS / modifier lines with
     units and CAD fees (from the clinic's fee-schedule XLSX).
  B) A payer prior-authorization letter body (only if the payer policy PDF
     shows the service requires PA).
  C) ``patient_plan`` — plain-language plan-of-care steps keyed to the
     clinic's treatment-protocol PDF.

MANDATORY workflow — use ONLY search_knowledge:
1. Start by running THIS BATCH of search_knowledge calls on
   ``folder_id=__CORPUS_FOLDER_ID__``:
   - "SOAP note lumbar radiculopathy patient"
   - "prior visit history patient"
   - "lumbar radiculopathy treatment protocol"
   - "prior authorization medical necessity"
   - "98941 CMT 3-4 regions fee"
   - "97012 mechanical traction fee"
   - "M54.16 radiculopathy lumbar"
   - "98940 98941 98942 CPT"
2. Every search_knowledge result has chunk_id + text. That is ENOUGH to
   produce the output — DO NOT call ``read``. The chunk's visible text
   is the ``supporting_phrase``.
3. Every ``Citation.chunk_id`` MUST be copied verbatim from a
   ``chunk_id`` returned by ``search_knowledge``.

Never use placeholders or "Unable to access" text. If a search returns
hits, USE THEM. The corpus contains: a SOAP note PDF for PT-4401 with
lumbar radiculopathy (ICD-10 M54.16), Sun Life chiropractic policy PDF,
Northside treatment protocols PDF, clinic fee-schedule XLSX, and
CPT/ICD-10 reference XLSX.
4. Coding rules:
   - ``code_type`` must be CPT / ICD-10 / HCPCS / MOD.
   - ``fee_citation`` must point to the fee-schedule XLSX chunk containing
     that code's row.
   - ``justification_citation`` must point to the SOAP note chunk that
     supports the code.
5. Prior auth:
   - Check the Sun Life medical policy carefully. Section B lists THREE
     triggers for required PA: (a) >12 visits in 12 months,
     (b) mechanical traction (CPT 97012), (c) treatment of lumbar
     radiculopathy. If ANY trigger applies, set
     ``prior_auth_required=True``.
   - Populate ``prior_auth_criteria`` with EVERY criterion from policy
     Section C (diagnosis, documented conservative therapy, objective
     findings, written care plan). For each, cite the policy chunk AND
     the chart chunk documenting the criterion is met.
   - ``prior_auth_letter_body`` must be payer-ready prose, not a template.
6. Patient plan:
   - Each step cites the treatment-protocols PDF.
   - Plain-language (Grade-8 reading level), no CPT codes in the patient
     instruction.

Do not fabricate codes, fees, or payer rules.
Do not call ``list_contents`` or ``read_around`` — they are unreliable in
this tenant. Rely on ``search_knowledge`` and ``read`` only.
"""


async def run_autopilot(
    *,
    patient_id: str,
    visit_date: str,
    corpus_folder_id: str,
    model: str,
) -> VisitAutopilotOutput:
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
    system = SYSTEM_TEMPLATE.replace("__CORPUS_FOLDER_ID__", corpus_folder_id).replace(
        "__PATIENT_ID__", patient_id
    )
    agent = Agent(
        model=f"openai:{model}",
        mcp_servers=[mcp],
        system_prompt=system,
        output_type=VisitAutopilotOutput,
        retries=3,
    )
    prompt = f"Patient: {patient_id}. Visit date: {visit_date}. Produce the full autopilot output."
    async with agent.run_mcp_servers():
        result = await agent.run(prompt, usage_limits=UsageLimits(request_limit=200))
    return getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[return-value]
