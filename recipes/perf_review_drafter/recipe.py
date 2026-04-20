"""Perf review drafter — employee + period → cited review draft.

Pain point: Managers write reviews from memory. This recipe pulls citable
evidence from 1:1 notes, project retros, peer feedback; structures it against
your competency rubric; and drafts a review anchored in specifics.

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

CORPUS = os.environ.get("HR_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class CompetencyScore(BaseModel):
    competency: str = Field(..., max_length=120)
    rating: str = Field(..., pattern="^(below|meets|exceeds|greatly_exceeds)$")
    evidence: str = Field(..., max_length=500)
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


class PerfReview(BaseModel):
    employee: str
    period: str
    overall: str = Field(..., pattern="^(below|meets|exceeds|greatly_exceeds)$")
    competencies: list[CompetencyScore] = Field(..., min_length=3, max_length=8)
    growth_areas: list[str] = Field(..., min_length=1, max_length=4)


PROMPT = (
    "You draft performance reviews. Anchor every claim in 1:1 notes, project "
    f"retros, or peer feedback from path_part_id={CORPUS}. Avoid adjectives "
    "without evidence. chunk_ids must be real."
)


async def run(employee: str, period: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=PerfReview)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Employee: {employee}\nPeriod: {period}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--employee", required=True)
    p.add_argument("--period", default="H1 2026")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.employee, args.period))


if __name__ == "__main__":
    main()
