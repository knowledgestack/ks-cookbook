"""QBR deck outline — customer → cited outline for a quarterly business review.

Pain point: CSMs rebuild the same QBR deck every quarter from scratch. This
recipe produces a slide-level outline (agenda, wins, risks, roadmap tie-ins,
asks) with citations per slide from past QBRs and success plans.

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

CORPUS = os.environ.get("CS_NOTES_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Slide(BaseModel):
    title: str = Field(..., max_length=80)
    bullets: list[str] = Field(..., min_length=1, max_length=6)
    citations: list[Citation] = Field(default_factory=list, max_length=3)


class QBROutline(BaseModel):
    account: str
    quarter: str
    slides: list[Slide] = Field(..., min_length=5, max_length=10)
    asks: list[str] = Field(default_factory=list, max_length=4)


PROMPT = (
    "You outline a QBR deck. Slides: Agenda, Wins, Usage & Adoption, Open Risks, "
    "Roadmap Alignment, Success Plan Update, Asks. Ground every slide in "
    f"path_part_id={CORPUS}. Citations are real chunk_ids."
)


async def run(account: str, quarter: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=QBROutline)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Account: {account}\nQuarter: {quarter}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--account", required=True)
    p.add_argument("--quarter", default="Q2 2026")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.account, args.quarter))


if __name__ == "__main__":
    main()
