"""Month-end close narrative — period → cited CFO-memo-style narrative.

Pain point: Controllers write the same month-end narrative for the CFO every
month (variance, accruals, reclass memos). This recipe pulls the trial
balance commentary + flux analysis notes from your corpus and drafts a
cited CFO memo.

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


class Variance(BaseModel):
    account: str
    actual_vs_budget: str = Field(..., max_length=160)
    driver: str = Field(..., max_length=300)
    citation: Citation


class CloseMemo(BaseModel):
    period: str
    tl_dr: str = Field(..., max_length=600)
    material_variances: list[Variance] = Field(..., min_length=1, max_length=10)
    accruals_and_reclass: list[str] = Field(default_factory=list, max_length=8)
    open_items: list[str] = Field(default_factory=list, max_length=6)


PROMPT = (
    "You draft month-end close memos. Material variances cite real chunk_ids "
    f"from path_part_id={CORPUS}. Do not invent numbers — use what's in the "
    "trial balance commentary + flux notes."
)


async def run(period: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=CloseMemo)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Period: {period}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--period", default="March 2026")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.period))


if __name__ == "__main__":
    main()
