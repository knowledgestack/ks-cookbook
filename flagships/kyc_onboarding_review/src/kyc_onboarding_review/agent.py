"""pydantic-ai agent that reviews a KYC onboarding application against policy."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.settings import ModelSettings

from kyc_onboarding_review.schema import KYCReview

SYSTEM_TEMPLATE = """\
You are a BSA/AML compliance analyst at Acme National Bank. Review the customer
onboarding application below against the bank's KYC/CDD policy and the
applicable federal regulations available in the Knowledge Stack corpus.

MANDATORY workflow:
1. __DISCOVERY_STEP__
2. Read the **acme_bank_kyc_policy** document first — it contains the
   onboarding checklist and risk tier definitions you must evaluate against.
3. Read the **sample_customer_application** document — it contains the
   customer's submitted information and documents.
4. If needed for specific regulatory citations, read the
   **beneficial_ownership_31cfr1010_230** or
   **ffiec_cdd_examination_procedures** documents.
5. Use the UUID ``path_part_id`` value from list_contents for each ``read``
   call. Do NOT use document names as UUIDs.
6. The ``read`` output contains ``[chunk:<uuid>]`` markers after each passage.
   Every ``Citation.chunk_id`` you emit MUST be copied verbatim from one of
   those markers.
4. Produce the structured ``KYCReview``:

   a. **Checklist**: For each CDD requirement in the bank's policy (individual
      customer requirements, legal entity requirements, beneficial ownership),
      check whether the customer application includes the required document or
      information. Mark each as PRESENT, MISSING, or INCOMPLETE.

   b. **Risk tier**: Assign LOW, MEDIUM, HIGH, or PROHIBITED based on the risk
      tier criteria in the bank's policy. Consider: industry type, geographic
      risk, transaction volume, ownership complexity, PEP status.

   c. **Risk factors**: List all risk-elevating factors found in the
      application (import/export, international wires, non-resident owners,
      commodity trading, etc.).

   d. **EDD required**: If the risk tier is HIGH, EDD is required per policy.
      List the specific EDD steps that must be completed.

   e. **Pending items**: List all documents or verifications that are still
      missing and must be resolved before account opening.

   f. **Recommendation**: Based on completeness and risk, recommend one of:
      APPROVE, APPROVE WITH CONDITIONS, DECLINE, ESCALATE TO BSA OFFICER.

Do not fabricate facts about the customer. If information is not in the
application, mark the corresponding checklist item as MISSING.

KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs or path_part_id filters.
2. search_knowledge returns hits with chunk_id and path_part_id; the text field is empty by design. Call read(path_part_id=<hit's path_part_id>) to get chunk content. The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read; it 404s.
3. Build every output field ONLY from chunk text you read. Never fabricate.
4. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() metadata or materialized_path), snippet (verbatim ≤240 chars).

Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones.
"""


async def review_kyc(
    *,
    corpus_folder_id: str | None,
    model: str,
) -> KYCReview:
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
    if corpus_folder_id:
        discovery_step = (
            f'Call ``list_contents(folder_id="{corpus_folder_id}")`` to '
            "enumerate the available documents."
        )
    else:
        discovery_step = (
            "Do NOT call ``list_contents``. Use ``find`` to locate the bank "
            "KYC policy, the sample customer application, and supporting "
            "regulations by title keywords such as ``kyc``, ``cdd``, "
            "``beneficial ownership``, and ``verdant``."
        )
    agent = Agent(
        model=f"openai:{model}",
        mcp_servers=[mcp],
        system_prompt=SYSTEM_TEMPLATE.replace("__DISCOVERY_STEP__", discovery_step),
        output_type=KYCReview,
        model_settings=ModelSettings(max_tokens=4096),
    )
    review: KYCReview | None = None
    try:
        async with agent.run_mcp_servers():
            result = await agent.run(
                "Review the Verdant Sourcing Group LLC onboarding application. "
                "Check every CDD requirement against the submitted documents, "
                "assign the risk tier, and produce the full KYC review."
            )
            review = getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[assignment]
    except BaseExceptionGroup as eg:
        # pydantic-ai's MCPServerStdio raises BrokenResourceError during
        # cleanup after the result is already produced. Safe to swallow
        # if we already have a result. Re-raise if we don't.
        if review is None:
            # Filter: only re-raise non-BrokenResource exceptions
            non_broken = [
                e
                for e in eg.exceptions
                if "BrokenResource" not in type(e).__name__
                and not (
                    isinstance(e, BaseExceptionGroup)
                    and all(
                        "BrokenResource" in type(sub).__name__
                        or "ClosedResource" in type(sub).__name__
                        for sub in (e.exceptions if hasattr(e, "exceptions") else [e])
                    )
                )
            ]
            if non_broken:
                raise
    except Exception:
        if review is None:
            raise
    if review is None:
        raise RuntimeError("Agent did not produce a result before the MCP session closed.")
    return review
