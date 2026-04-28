"""Changelog from commits — commit summaries → cited user-facing changelog.

Pain point: Engineers write dense commits; users need the "what changed,
why you care" version. This recipe takes raw commit messages and asks
Knowledge Stack about your product docs / security policies for context,
then produces a Keep-A-Changelog–style entry list with citations where
the change touches documented behavior.

Framework: pydantic-ai. KS access via the knowledgestack-mcp stdio server.
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
    "You turn raw commits into a Keep-A-Changelog–style user-facing "
    "changelog. Knowledge Stack is your search backend; ask it natural-"
    "language questions about your product docs, security policy, and "
    "architecture when a commit touches documented behavior.\n\n"
    "Workflow:\n"
    "1. Read the commit list. Skip pure chore/refactor/test/deps bumps "
    "unless they affect security or behavior visible to users.\n"
    "2. For each kept commit, categorize (Added / Changed / Fixed / "
    "Removed / Security) and write a user-facing summary + 'why_user_"
    "cares' line.\n"
    "3. When a commit touches documented behavior (zero-trust, GDPR, "
    "auth, ingestion, RBAC), ask Knowledge Stack for context, e.g.:\n"
    "   • 'What does our security policy say about session token "
    "rotation?'\n"
    "   • 'How does GDPR erasure work in our system?'\n"
    "   Frame queries naturally. Never use folder UUIDs or path_part_id "
    "filters.\n"
    "4. search_knowledge returns hits with chunk_id and path_part_id; "
    "the text field is empty. Call read(path_part_id=<hit's "
    "path_part_id>) to get the chunk text. The trailing [chunk:<uuid>] "
    "marker is your citation.chunk_id (NEVER pass chunk_id to read; "
    "it 404s).\n"
    "5. Populate every citation with chunk_id (verbatim), document_name "
    "(filename in read() metadata), and snippet (verbatim ≤240 chars). "
    "Citations are optional — only attach when a doc actually grounds "
    "the change."
    """Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""
)
async def run(version: str, date: str, commits_file: Path) -> None:
    commits_text = commits_file.read_text()
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", ".venv/bin/ks-mcp"),
        args=(os.environ.get("KS_MCP_ARGS", "") or "").split(),
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o')}",
        mcp_servers=[mcp],
        system_prompt=PROMPT,
        output_type=Changelog,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Version: {version}\nDate: {date}\n\nCommits:\n{commits_text[:8000]}"
        )
    print(json.dumps(result.output.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--version", required=True)
    p.add_argument("--date", required=True)
    p.add_argument(
        "--commits-file",
        type=Path,
        required=True,
        help="Text file with commit subjects (one per line).",
    )
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.version, args.date, args.commits_file))


if __name__ == "__main__":
    main()
