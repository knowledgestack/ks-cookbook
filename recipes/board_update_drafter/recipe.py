"""Board update drafter — period → cited board update draft.

Pain point: Founders write the monthly update from scratch, every time. This
recipe produces a structured draft (highlights, KPIs, risks, asks) grounded
in your OKR tracker, sales notes, and incident list with citations.

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

CORPUS = os.environ.get("BOARD_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class BoardUpdate(BaseModel):
    period: str
    tl_dr: str = Field(..., max_length=600)
    highlights: list[str] = Field(..., min_length=2, max_length=6)
    kpis: list[str] = Field(..., min_length=2, max_length=8)
    risks: list[str] = Field(..., min_length=1, max_length=5)
    asks: list[str] = Field(default_factory=list, max_length=4)
    citations: list[Citation] = Field(..., min_length=2, max_length=10)


PROMPT = (
    f"You draft a board update. Pull highlights, KPIs, risks from "
    f"path_part_id={CORPUS}. Every number must cite a real chunk_id. No spin."
)


async def run(period: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=BoardUpdate)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Period: {period}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--period", default="March 2026")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.period))


if __name__ == "__main__":
    main()
