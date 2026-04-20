"""Competitive positioning — competitor name → cited win/loss positioning sheet.

Pain point: AEs on a live call Slack-ping the PMM team for "how do we position
against X?" every single time. This recipe returns a cited sheet: their
strengths, our counters, traps to avoid.

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

CORPUS = os.environ.get("COMPETE_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Position(BaseModel):
    competitor: str
    their_strengths: list[str] = Field(..., min_length=1, max_length=6)
    their_weaknesses: list[str] = Field(..., min_length=1, max_length=6)
    our_counters: list[str] = Field(..., min_length=2, max_length=8)
    traps_to_avoid: list[str] = Field(default_factory=list, max_length=4)
    citations: list[Citation] = Field(..., min_length=2, max_length=8)


PROMPT = (
    "You brief an AE on live-call positioning. Read battlecards, win/loss "
    f"notes, and compete briefs in path_part_id={CORPUS}. Be honest about "
    "their strengths; no spin. Every claim cites a real chunk_id."
)


async def run(competitor: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=Position)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Competitor: {competitor}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--competitor", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.competitor))


if __name__ == "__main__":
    main()
