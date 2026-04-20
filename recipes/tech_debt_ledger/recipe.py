"""Tech debt ledger — area keyword → cited prioritized tech-debt list.

Pain point: Tech debt lives in Slack threads and retros, never in a ledger. By
review time nobody remembers what to pay down. This recipe mines your retros /
design docs for debt items, ranks by severity, and cites sources.

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


class DebtItem(BaseModel):
    title: str = Field(..., max_length=120)
    impact: str = Field(..., pattern="^(low|medium|high|critical)$")
    effort: str = Field(..., pattern="^(S|M|L|XL)$")
    description: str = Field(..., max_length=400)
    citations: list[Citation] = Field(..., min_length=1, max_length=3)


class DebtLedger(BaseModel):
    area: str
    items: list[DebtItem] = Field(..., min_length=1, max_length=30)


PROMPT = (
    "You mine tech debt from retros, post-mortems, design docs, and ADRs in "
    f"path_part_id={CORPUS}. Rank by impact × effort. Each item cites real "
    "chunk_ids. Do not invent items."
)


async def run(area: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=DebtLedger)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Area: {area}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--area", required=True, help="e.g. 'ingestion pipeline'")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.area))


if __name__ == "__main__":
    main()
