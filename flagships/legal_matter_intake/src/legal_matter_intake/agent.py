"""pydantic-ai agent that produces a Sertain matter intake dossier."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.usage import UsageLimits

from legal_matter_intake.schema import MatterIntakeDossier

SYSTEM_TEMPLATE = """\
You are the intake partner at Harbour & Finch LLP (a Sertain customer). A
new client and matter have come in. Produce a complete intake dossier,
grounded in the firm's MCP corpus:
  - Conflicts database (XLSX)  — every row is a prior client matter.
  - Practice-area risk playbook (PDF) — partner-authored risk rules.
  - Jurisdiction rules (PDF) — e.g. LSO professional conduct for Ontario.
  - Fee schedule (XLSX) — hourly rates by practice area & seniority.
  - Engagement letter template (PDF).

MANDATORY workflow — use ONLY these tools:
1. Call ``search_knowledge`` with ``folder_id=your tenant (use search_knowledge — no folder_id needed)`` for
   each relevant topic. Run multiple searches to cover:
   - Conflicts: search for the client name and any adverse parties/related
     entities named in the matter (e.g. "Northstar Biotech", "MIT TLO").
   - Practice-area risk: search for keywords from the matter (e.g.
     "Series B financing", "license-in university", "constructive dismissal").
   - Jurisdiction rules: search for "conflict of interest", "former client",
     "fees and disbursements".
   - Fee schedule: search for the practice area name.
2. Optionally ``read`` a chunk's ``path_part_id`` when you need more context
   around a search hit.
3. Every ``Citation.chunk_id`` MUST be copied verbatim from a ``chunk_id``
   returned by ``search_knowledge`` or a ``[chunk:<uuid>]`` marker in
   ``read`` output. Do NOT invent UUIDs.
4. Populate the ``MatterIntakeDossier``:
   - ``conflicts_analysis``: one entry per adverse party / related entity
     checked. If no hit, you may omit or include with ``hit_type=none``.
   - ``risk_factors``: cite the playbook; cover regulatory, counterparty,
     and scope/scope-creep risks.
   - ``fee_estimate``: use the XLSX fee schedule for rates; propose a
     realistic staffing model (partner/associate/paralegal blend).
   - ``required_disclosures``: cite specific rule numbers in the
     jurisdiction PDF.
   - ``recommended_engagement_terms``: concrete clauses to include/modify
     versus the firm's template (retainer, scope, termination).

Do not fabricate rates, rule numbers, or prior matters.
Do not call ``list_contents`` or ``read_around`` — they are unreliable in
this tenant. Rely on ``search_knowledge`` and ``read`` only.

KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs or path_part_id filters.
2. search_knowledge returns hits with chunk_id and path_part_id; the text field is empty by design. Call read(path_part_id=<hit's path_part_id>) to get chunk content. The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read; it 404s.
3. Build every output field ONLY from chunk text you read. Never fabricate.
4. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() metadata or materialized_path), snippet (verbatim ≤240 chars).

Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones.
"""


async def produce_dossier(
    *,
    client: str,
    matter: str,
    corpus_folder_id: str,
    model: str,
) -> MatterIntakeDossier:
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
        output_type=MatterIntakeDossier,
        retries=3,
    )
    prompt = f"Client: {client}\nMatter: {matter}\nProduce the full intake dossier."
    async with agent.run_mcp_servers():
        result = await agent.run(prompt, usage_limits=UsageLimits(request_limit=200))
    return getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[return-value]
