"""On-call shadow plan — team + new engineer → cited ramp plan for on-call.

Pain point: New engineers get thrown into the pager with no structured shadow.
This recipe builds a 4-week shadow plan grounded in your on-call policy,
runbooks, and past incidents.

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

CORPUS = os.environ.get("ENG_DOCS_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Week(BaseModel):
    week_number: int = Field(..., ge=1, le=8)
    focus: str = Field(..., max_length=200)
    activities: list[str] = Field(..., min_length=2, max_length=6)
    graduation_criteria: str = Field(..., max_length=240)


class ShadowPlan(BaseModel):
    team: str
    engineer: str
    weeks: list[Week] = Field(..., min_length=3, max_length=6)
    citations: list[Citation] = Field(..., min_length=1, max_length=6)


PROMPT = (
    "You build on-call ramp plans. Read the on-call policy, runbook index, and "
    f"recent incident summaries in path_part_id={CORPUS}. Grad criteria must be "
    "observable. chunk_ids must be real."
)


async def run(team: str, engineer: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=ShadowPlan)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Team: {team}\nEngineer: {engineer}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--team", required=True)
    p.add_argument("--engineer", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.team, args.engineer))


if __name__ == "__main__":
    main()
