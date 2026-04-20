"""PIP drafter — employee + concerns → cited performance improvement plan.

Pain point: PIPs must be specific, measurable, time-bound, and consistent with
HR policy. Managers produce vague ones that don't hold up. This recipe drafts a
cited PIP tied to your performance policy and rubric.

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


class PIPGoal(BaseModel):
    area: str = Field(..., max_length=120)
    measurable_target: str = Field(..., max_length=300)
    by_date: str = Field(..., max_length=40)
    support_from_manager: str = Field(..., max_length=200)


class PIP(BaseModel):
    employee: str
    duration_weeks: int = Field(..., ge=4, le=12)
    concerns_summary: str = Field(..., max_length=600)
    goals: list[PIPGoal] = Field(..., min_length=2, max_length=5)
    check_in_cadence: str = Field(..., max_length=120)
    citations: list[Citation] = Field(..., min_length=2, max_length=6)


PROMPT = (
    "You draft performance improvement plans per company policy. Goals must "
    f"be SMART. Cite real chunk_ids from HR policy in path_part_id={CORPUS}. "
    "Default duration: 8 weeks unless policy says otherwise."
)


async def run(employee: str, concerns: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=PIP)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Employee: {employee}\nConcerns: {concerns}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--employee", required=True)
    p.add_argument("--concerns", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.employee, args.concerns))


if __name__ == "__main__":
    main()
