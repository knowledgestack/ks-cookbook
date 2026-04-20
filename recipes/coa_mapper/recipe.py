"""Chart-of-accounts mapper — source COA CSV → cited target-system mapping.

Pain point: Migrating QuickBooks → NetSuite (or any re-chart) means mapping
every account by hand. This recipe reads both chart docs from your corpus and
emits a line-by-line mapping with confidence and a citation for each.

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

CORPUS = os.environ.get("FINANCE_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class AccountMapping(BaseModel):
    source_account: str
    target_account: str
    confidence: str = Field(..., pattern="^(low|medium|high)$")
    reason: str = Field(..., max_length=300)
    needs_human_review: bool
    citation: Citation


class COAMap(BaseModel):
    source_system: str
    target_system: str
    mappings: list[AccountMapping] = Field(..., min_length=1, max_length=50)


PROMPT = (
    f"You map accounts between charts. Read both COA docs in "
    f"path_part_id={CORPUS}. Low confidence → needs_human_review=true. "
    "chunk_ids must be real — never guess account numbers."
)


async def run(csv_path: Path, source: str, target: str) -> None:
    accounts = csv_path.read_text()[:6000]
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=COAMap)
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Source: {source}\nTarget: {target}\n\nSource accounts:\n{accounts}"
        )
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv", type=Path, required=True, help="CSV of source account numbers + names.")
    p.add_argument("--source", default="QuickBooks")
    p.add_argument("--target", default="NetSuite")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.csv, args.source, args.target))


if __name__ == "__main__":
    main()
