"""CSAT theme mining — period → cited themes from support surveys + tickets.

Pain point: CX leaders skim 500 CSAT comments and recall the last three. This
recipe clusters themes across the corpus (survey exports, ticket summaries),
cites representative chunks, and suggests priority fixes.

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

CORPUS = os.environ.get("KB_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Theme(BaseModel):
    theme: str = Field(..., max_length=120)
    sentiment: str = Field(..., pattern="^(positive|mixed|negative)$")
    frequency_estimate: str = Field(..., max_length=80)
    representative_quote: str = Field(..., max_length=300)
    suggested_fix: str = Field(..., max_length=300)
    citations: list[Citation] = Field(..., min_length=2, max_length=4)


class ThemeReport(BaseModel):
    period: str
    themes: list[Theme] = Field(..., min_length=3, max_length=10)
    headline: str = Field(..., max_length=400)


PROMPT = (
    f"You mine CX themes from surveys + tickets in path_part_id={CORPUS}. "
    "Cluster, don't list. Every theme cites ≥2 real chunk_ids. No made-up "
    "percentages."
)


async def run(period: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=ThemeReport)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Period: {period}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--period", default="Q1 2026")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.period))


if __name__ == "__main__":
    main()
