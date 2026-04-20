"""Changelog from commits — commit summaries → cited user-facing changelog.

Pain point: Engineers write dense commits; users need the "what changed, why
you care" version. This recipe pairs commit messages with product docs from
your corpus so the changelog links each item to feature/policy context.

Framework: pydantic-ai. Tools: list_contents, search_knowledge, read.
Output: stdout (JSON).
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

CORPUS = os.environ.get("ENG_DOCS_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class ChangelogEntry(BaseModel):
    category: str = Field(..., pattern="^(Added|Changed|Fixed|Removed|Security)$")
    summary: str = Field(..., max_length=200)
    why_user_cares: str = Field(..., max_length=240)
    citations: list[Citation] = Field(default_factory=list, max_length=3)


class Changelog(BaseModel):
    version: str
    date: str
    entries: list[ChangelogEntry] = Field(..., min_length=1, max_length=30)


PROMPT = (
    "You turn raw commits into a user-facing changelog. For each notable change, "
    "categorize (Keep A Changelog style), write a user-facing summary and 'why "
    f"you care' line. When a product doc in path_part_id={CORPUS} gives "
    "context (policy, feature spec), cite the real chunk_id. Omit chore/refactor."
)


async def run(version: str, date: str, commits_file: Path) -> None:
    commits_text = commits_file.read_text()
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=Changelog)
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Version: {version}\nDate: {date}\n\nCommits:\n{commits_text[:8000]}"
        )
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--version", required=True)
    p.add_argument("--date", required=True)
    p.add_argument("--commits-file", type=Path, required=True,
                   help="Text file with commit subjects (one per line).")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.version, args.date, args.commits_file))


if __name__ == "__main__":
    main()
