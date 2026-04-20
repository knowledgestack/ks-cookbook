"""MLS-listing valuation — listing → cited comps-based valuation range.

Pain point: Agents + appraisers pull comps manually. This recipe reads
recent comparable sales from your MLS corpus and returns a valuation range
with the 3-5 anchor comps cited.

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

CORPUS = os.environ.get("REAL_ESTATE_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Comp(BaseModel):
    address: str
    sold_price: str
    sold_date: str = Field(..., max_length=40)
    sqft_delta_pct: float
    adjustment_rationale: str = Field(..., max_length=300)
    citation: Citation


class Valuation(BaseModel):
    subject_address: str
    low_estimate: str
    likely_estimate: str
    high_estimate: str
    comps: list[Comp] = Field(..., min_length=3, max_length=8)
    confidence: str = Field(..., pattern="^(low|medium|high)$")
    caveats: str = Field(..., max_length=400)


PROMPT = (
    "You value a residential listing from comparable sales in "
    f"path_part_id={CORPUS}. Use only actually-sold comps within 6 months + "
    "1 mile. Adjust for sqft and condition. chunk_ids must be real."
)


async def run(subject: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=Valuation)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Subject: {subject}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--subject", required=True,
                   help="Subject address (e.g. '123 Elm St, Springfield, IL').")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.subject))


if __name__ == "__main__":
    main()
