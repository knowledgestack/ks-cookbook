"""Case study drafter — customer → cited case-study draft.

Pain point: Case studies are bottlenecked on PMM. Customer notes and metrics
live across QBRs and call transcripts. This recipe assembles a structured
draft (challenge, solution, results) with chunk citations.

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


class CaseStudyDraft(BaseModel):
    customer: str
    hero_stat: str = Field(..., max_length=160)
    challenge: str = Field(..., max_length=800)
    solution: str = Field(..., max_length=800)
    results: list[str] = Field(..., min_length=2, max_length=6)
    pull_quote: str = Field(..., max_length=300)
    citations: list[Citation] = Field(..., min_length=3, max_length=8)


PROMPT = (
    "You draft case studies. Pull challenge/solution/results from QBRs, call "
    f"notes, and success plans in path_part_id={CORPUS}. No invented metrics. "
    "The pull-quote must come from actual customer words. chunk_ids must be real."
)


async def run(customer: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=CaseStudyDraft)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Customer: {customer}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--customer", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.customer))


if __name__ == "__main__":
    main()
