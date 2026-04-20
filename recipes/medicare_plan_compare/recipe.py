"""Medicare supplement plan-compare — beneficiary profile → cited compare table.

Pain point: Beneficiaries (and their brokers) compare Medigap / Advantage
plans across premium, out-of-pocket, network, and drug formulary. This recipe
pulls the plans from your corpus and returns a cited side-by-side table.

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

CORPUS = os.environ.get("MEDICARE_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class PlanCompareRow(BaseModel):
    plan_name: str
    plan_type: str = Field(..., pattern="^(medigap|advantage|part_d|special_needs)$")
    monthly_premium: str
    moop: str = Field(..., max_length=120, description="Max out-of-pocket.")
    network_note: str = Field(..., max_length=200)
    formulary_note: str = Field(..., max_length=200)
    citation: Citation


class PlanComparison(BaseModel):
    beneficiary_profile: str
    plans: list[PlanCompareRow] = Field(..., min_length=2, max_length=8)
    narrative: str = Field(..., max_length=600)


PROMPT = (
    f"You build Medicare plan comparisons from path_part_id={CORPUS}. Never "
    "invent premiums or network restrictions — quote from the plan documents. "
    "chunk_ids must be real."
)


async def run(profile: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=PlanComparison)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Profile: {profile}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profile", required=True,
                   help="e.g. '67yo, Medicare A+B, OC CA, metformin'")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.profile))


if __name__ == "__main__":
    main()
