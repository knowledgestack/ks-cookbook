"""Migration guide drafter — from/to versions → cited step-by-step migration.

Pain point: Customers ping support asking how to move from v3 → v4. Eng writes
the same guide from scratch every time. This recipe reads release notes +
upgrade docs in your corpus and produces a structured migration guide with
citations.

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


class MigrationStep(BaseModel):
    step: str = Field(..., max_length=200)
    detail: str = Field(..., max_length=600)
    breaking: bool
    rollback: str = Field(..., max_length=200)
    citation: Citation


class MigrationGuide(BaseModel):
    from_version: str
    to_version: str
    preflight: list[str] = Field(..., min_length=1, max_length=6)
    steps: list[MigrationStep] = Field(..., min_length=2, max_length=15)
    postflight: list[str] = Field(..., min_length=1, max_length=6)


PROMPT = (
    "You draft version migration guides. Ground every step in release notes, "
    f"changelogs, or upgrade docs from path_part_id={CORPUS}. Flag breaking "
    "changes explicitly and include a per-step rollback. Cite real chunk_ids."
)


async def run(from_v: str, to_v: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=MigrationGuide)
    async with agent.run_mcp_servers():
        result = await agent.run(f"From: {from_v}\nTo: {to_v}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--from-version", required=True, dest="from_v")
    p.add_argument("--to-version", required=True, dest="to_v")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.from_v, args.to_v))


if __name__ == "__main__":
    main()
