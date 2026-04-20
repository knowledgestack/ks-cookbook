"""Expense policy violation check — expense line → cited verdict.

Pain point: Finance reviewers eyeball expense reports against a 40-page T&E
policy. This recipe classifies each line (allowed / out-of-policy / needs
receipt / needs approval) and cites the exact policy section.

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

CORPUS = os.environ.get("FINANCE_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class ExpenseVerdict(BaseModel):
    description: str
    amount: str
    category: str
    verdict: str = Field(..., pattern="^(allowed|out_of_policy|needs_receipt|needs_approval)$")
    reason: str = Field(..., max_length=400)
    citations: list[Citation] = Field(..., min_length=1, max_length=3)


PROMPT = (
    f"You review expense reports vs our T&E policy in path_part_id={CORPUS}. "
    "Apply per-category caps, receipt thresholds, and pre-approval rules. "
    "chunk_ids must be real."
)


async def run(description: str, amount: str, category: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=ExpenseVerdict)
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Description: {description}\nAmount: {amount}\nCategory: {category}"
        )
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--description", required=True)
    p.add_argument("--amount", required=True)
    p.add_argument("--category", required=True, help="e.g. meals, travel, entertainment")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.description, args.amount, args.category))


if __name__ == "__main__":
    main()
