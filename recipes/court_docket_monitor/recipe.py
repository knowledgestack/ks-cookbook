"""Court-docket monitor — party + period → cited litigation activity summary.

Pain point: Legal + strategy teams want to know "has <competitor> been sued
in N.D. Cal. this quarter?" without paying for PACER monitoring. This recipe
reads your ingested docket filings and returns a cited summary per party.

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

CORPUS = os.environ.get("DOCKET_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class DocketEntry(BaseModel):
    case_caption: str = Field(..., max_length=240)
    court: str = Field(..., max_length=120)
    filed: str = Field(..., max_length=40)
    nature_of_suit: str = Field(..., max_length=120)
    role: str = Field(..., pattern="^(plaintiff|defendant|amicus|other)$")
    status: str = Field(..., max_length=120)
    citation: Citation


class DocketReport(BaseModel):
    party: str
    period: str
    entries: list[DocketEntry] = Field(default_factory=list, max_length=50)
    headline: str = Field(..., max_length=400)


PROMPT = (
    "You summarize litigation activity for a named party. Only include cases "
    f"actually documented in path_part_id={CORPUS}. Never invent case "
    "captions. chunk_ids must be real."
)


async def run(party: str, period: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=DocketReport)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Party: {party}\nPeriod: {period}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--party", required=True, help="Company or individual name.")
    p.add_argument("--period", default="Q1 2026")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.party, args.period))


if __name__ == "__main__":
    main()
