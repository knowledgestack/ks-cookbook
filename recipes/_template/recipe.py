"""Recipe template — copy this directory to ``recipes/<your-name>/`` and edit.

Every recipe:
  1. Connects to the KS MCP server over stdio (see ``_shared/mcp_client.py``).
  2. Uses at least one MCP tool to ground its output.
  3. Emits cited output — either inline ``[chunk:<uuid>]`` tags, or a
     structured evidence section at the end.
  4. Stays under ~100 LOC. Optimize for readability.
  5. Runs via ``uv run python recipes/<your-name>/recipe.py <args>``.

Title: <one-line description of the B2B problem solved>
Tenant: any seeded tenant (default: pwuser1 personal tenant)
Framework: <OpenAI | Anthropic | pydantic-ai | LangGraph | raw MCP>
Pain point: <who feels this and why>
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Allow ``python recipes/<name>/recipe.py`` to find ``_shared``.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _shared.mcp_client import call, ks_mcp_session  # noqa: E402


async def run(topic: str) -> None:
    async with ks_mcp_session() as session:
        # Example: list root folders as a sanity check.
        folders_json = await call(session, "list_contents", {})
        print(folders_json)
        # …replace with real work, producing cited output.
        _ = topic


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--topic", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set. See repo README.")
    asyncio.run(run(args.topic))


if __name__ == "__main__":
    main()
