"""Basel III risk-weight calculator — exposure → cited RWA calculation.

Pain point: Credit risk teams look up Basel III risk weights manually (by
asset class, counterparty type, CRM). This recipe reads the Basel III rules
from your corpus and computes the risk-weighted asset (RWA) with citations.

Framework: pydantic-ai. Tools: list_contents, search_knowledge, read.
Output: stdout (JSON).
"""

import argparse
import asyncio
import json
import os
import sys

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

CORPUS = os.environ.get("REGULATORY_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class RWACalculation(BaseModel):
    exposure_name: str
    asset_class: str = Field(..., max_length=120)
    counterparty_type: str = Field(..., max_length=120)
    notional: str
    applied_risk_weight_pct: float = Field(..., ge=0, le=1250)
    rwa: str
    crm_applied: str = Field(..., max_length=240,
                             description="Credit-risk mitigation, if any.")
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


PROMPT = (
    f"You compute Basel III risk-weighted assets per the rules in "
    f"path_part_id={CORPUS}. Apply standardised approach unless corpus says "
    "otherwise. Every weight cites the rule's chunk_id."
)


async def run(name: str, asset_class: str, counterparty: str, notional: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=RWACalculation)
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Exposure: {name}\nAsset class: {asset_class}\n"
            f"Counterparty: {counterparty}\nNotional: {notional}"
        )
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--name", required=True, help="Exposure label.")
    p.add_argument("--asset-class", required=True)
    p.add_argument("--counterparty", required=True)
    p.add_argument("--notional", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.name, args.asset_class, args.counterparty, args.notional))


if __name__ == "__main__":
    main()
