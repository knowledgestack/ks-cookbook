"""pydantic-ai agent that reads a 10-K from KS and produces a risk-flag memo."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from earnings_risk_analyzer.schema import EarningsRiskMemo

SYSTEM = """\
You are a senior equity research analyst at a buy-side fund. Produce a
risk-flag memo for the filing stored in the Knowledge Stack tenant.

MANDATORY workflow — use ONLY these two tools:
1. ``list_contents(folder_id=your tenant (use search_knowledge — no folder_id needed))`` — enumerate the filings.
2. ``read(path_part_id=<filing UUID>, max_chars=6000)`` — read the filing text.
   It contains Risk Factors (Item 1A) and MD&A (Item 7). Each passage ends
   with an inline ``[chunk:<uuid>]`` marker.
3. Produce an ``EarningsRiskMemo`` with 5-10 risk flags, ordered by severity.

IMPORTANT: Do NOT call ``read_around``, ``search_knowledge``, ``search_keyword``,
``find``, or ``get_info``. Only use ``list_contents`` and ``read``.

Each RiskFlag MUST:
- Categorize the risk (Market / Competition / Operational / Regulatory / etc.)
- Assign a severity (CRITICAL / HIGH / MEDIUM / LOW) based on materiality
- Include >=1 citation with the ``chunk_id`` copied VERBATIM from a
  ``[chunk:...]`` marker in the read output
- Summarize what mitigation the company describes (or flag the absence)

Also identify risks that look NEW or materially changed vs a typical prior-year
10-K for a company in this industry — these are the most actionable for PMs.

End with ``investment_implications``: what should a portfolio manager take away?
Be specific (not "monitor risks" — name the exact downside scenario and its
probability framing).

Use the UUID path_part_id values from list_contents — NOT document names.
"""


async def analyze_10k(
    *,
    corpus_folder_id: str,
    model: str,
) -> EarningsRiskMemo:
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
        system_prompt=SYSTEM,
        output_type=EarningsRiskMemo,
    )
    memo: EarningsRiskMemo | None = None
    try:
        async with agent.run_mcp_servers():
            result = await agent.run(
                "Analyze the Cloudflare FY2025 10-K filing. Produce the full risk-flag memo."
            )
            memo = getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[assignment]
    except BaseExceptionGroup:
        # pydantic-ai's MCPServerStdio raises BrokenResourceError during
        # cleanup after the result is already produced. Safe to swallow.
        pass
    if memo is None:
        raise RuntimeError("Agent did not produce a result before the MCP session closed.")
    return memo
