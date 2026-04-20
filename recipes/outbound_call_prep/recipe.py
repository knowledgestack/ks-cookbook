"""Outbound call prep — prospect + call goal → cited 1-page prep sheet.

Pain point: SDRs book discovery calls and prep in Slack DMs. This recipe
produces a single-page prep: prospect context, hypothesis, 3 discovery
questions, potential objections, and next-step framing — all cited.

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

CORPUS = os.environ.get("SALES_NOTES_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class CallPrep(BaseModel):
    prospect: str
    goal: str
    context: str = Field(..., max_length=600)
    hypothesis: str = Field(..., max_length=400)
    discovery_questions: list[str] = Field(..., min_length=3, max_length=5)
    anticipated_objections: list[str] = Field(..., min_length=2, max_length=4)
    proposed_next_step: str = Field(..., max_length=240)
    citations: list[Citation] = Field(..., min_length=2, max_length=6)


PROMPT = (
    f"You build 1-page call preps. Context + hypothesis ground in "
    f"path_part_id={CORPUS} (past interactions, case studies, ICP notes). "
    "chunk_ids must be real."
)


async def run(prospect: str, goal: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=CallPrep)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Prospect: {prospect}\nGoal: {goal}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prospect", required=True)
    p.add_argument("--goal", default="qualify fit for discovery")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.prospect, args.goal))


if __name__ == "__main__":
    main()
