"""pydantic-ai agent that drafts a structured credit memo grounded in KS corpus."""

import os

from pydantic_ai import Agent
from pydantic_ai.usage import UsageLimits
from pydantic_ai.mcp import MCPServerStdio

from credit_memo_drafter.schema import CreditMemo

SYSTEM_TEMPLATE = """\
You are a commercial credit analyst at Riverway Bank. Draft a credit memo for the
loan request below, grounded strictly in the documents available under the
CORPUS folder via MCP tools.

MANDATORY workflow:
1. Call ``search_knowledge`` (no folder_id; whole tenant) to find
   the available documents (credit policy, borrower financials, borrower
   business plan, industry benchmarks).
2. Call ``read`` on EACH relevant document, using the UUID ``path_part_id``
   value from the list_contents response. Do NOT use document names as UUIDs.
3. The ``read`` output contains ``[chunk:<uuid>]`` markers after each passage.
   Every ``Citation.chunk_id`` you emit MUST be copied verbatim from one of
   those markers.
4. Produce the structured ``CreditMemo``:
   - ``risk_rating`` on the 1-9 scale defined in the credit policy.
   - ``risks`` must identify both quantitative (leverage, DSCR, concentration)
     and qualitative (management, market, regulatory) factors.
   - ``covenants`` must be specific and reference the bank's policy.
   - Flag any underwriting standards the deal DOES NOT meet under
     ``policy_exceptions``.

Do not fabricate numbers. If a figure is not in the financials, say so and
lower the confidence of that risk factor.

KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs or path_part_id filters.
2. search_knowledge returns hits with chunk_id and path_part_id; the text field is empty by design. Call read(path_part_id=<hit's path_part_id>) to get chunk content. The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read; it 404s.
3. Build every output field ONLY from chunk text you read. Never fabricate.
4. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() metadata or materialized_path), snippet (verbatim ≤240 chars).

Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones.
"""


async def draft_memo(
    *,
    borrower: str,
    loan_amount: int,
    corpus_folder_id: str,
    model: str,
) -> CreditMemo:
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
        output_type=CreditMemo,
        retries=4,
        output_retries=4,
    )
    prompt = (
        f"Loan request: ${loan_amount:,} senior secured term facility for "
        f"{borrower}. Draft the credit memo."
    )
    async with agent.run_mcp_servers():
        result = await agent.run(prompt, usage_limits=UsageLimits(request_limit=200))
    return getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[return-value]
