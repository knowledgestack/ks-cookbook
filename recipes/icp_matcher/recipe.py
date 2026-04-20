"""ICP matcher — score a prospect company against your Ideal Customer Profile.

Pain point: SDRs spend the first 20 minutes of every prospecting session
re-reading the ICP deck and guessing whether a company fits. This recipe:
company name + short blurb → fit score + cited criteria hits/misses.

Framework: pydantic-ai.
Tools used: list_contents, search_knowledge, read.
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

CORPUS = os.environ.get("ICP_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class CriterionHit(BaseModel):
    criterion: str = Field(..., max_length=120)
    verdict: str = Field(..., pattern="^(hit|miss|unclear)$")
    reason: str = Field(..., max_length=240)
    citations: list[Citation] = Field(..., min_length=1, max_length=3)


class ICPMatch(BaseModel):
    company: str
    fit_score: int = Field(..., ge=0, le=100)
    tier: str = Field(..., pattern="^(A|B|C|disqualified)$")
    criteria: list[CriterionHit] = Field(..., min_length=3, max_length=10)
    next_step: str = Field(..., max_length=240)


PROMPT = (
    "You are an SDR ops analyst. Using the ICP criteria, segmentation, and "
    f"disqualification notes in path_part_id={CORPUS}, score the prospect. "
    "Read the actual ICP doc before scoring. Every criterion must cite real "
    "chunk_ids from read output. Fit < 40 → disqualified; 40-65 → C; 65-80 → B; "
    ">80 → A."
)


async def run(company: str, blurb: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
        mcp_servers=[mcp], system_prompt=PROMPT, result_type=ICPMatch,
    )
    request = f"Company: {company}\nBlurb: {blurb}"
    async with agent.run_mcp_servers():
        result = await agent.run(request)
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--company", required=True)
    p.add_argument("--blurb", default="B2B SaaS, ~200 employees, US-based.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.company, args.blurb))


if __name__ == "__main__":
    main()
