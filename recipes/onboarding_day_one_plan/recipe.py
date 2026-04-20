"""Onboarding day-one plan — role → cited day-one / week-one plan.

Pain point: Managers re-invent onboarding for every hire. This recipe pulls
the company onboarding policy + role-specific learning plan and produces a
day-one and week-one task list with citations.

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


class Task(BaseModel):
    task: str = Field(..., max_length=200)
    owner: str = Field(..., max_length=60, description="hire | manager | IT | HR")


class OnboardingPlan(BaseModel):
    role: str
    day_one: list[Task] = Field(..., min_length=4, max_length=12)
    week_one: list[Task] = Field(..., min_length=4, max_length=12)
    first_30_days: list[Task] = Field(..., min_length=3, max_length=8)
    citations: list[Citation] = Field(..., min_length=1, max_length=5)


PROMPT = (
    "You plan onboarding. Pull day-one required steps, role-specific training, "
    f"and tooling access from path_part_id={CORPUS}. Assign owners. chunk_ids "
    "must be real."
)


async def run(role: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=OnboardingPlan)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Role: {role}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--role", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.role))


if __name__ == "__main__":
    main()
