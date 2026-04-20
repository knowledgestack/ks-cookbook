"""Account research brief — account name → cited pre-call prep sheet.

Pain point: AEs rebuild the same prep doc for every call: past touchpoints,
product fit, objections, champion map. This recipe pulls it from your corpus
(call notes, past proposals, product docs) with chunk citations.

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

CORPUS = os.environ.get("ACCOUNT_NOTES_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class AccountBrief(BaseModel):
    account: str
    summary: str = Field(..., max_length=600)
    recent_activity: list[str] = Field(default_factory=list, max_length=6)
    known_objections: list[str] = Field(default_factory=list, max_length=6)
    product_fit: list[str] = Field(default_factory=list, max_length=6)
    recommended_next_step: str = Field(..., max_length=240)
    citations: list[Citation] = Field(..., min_length=2, max_length=8)


PROMPT = (
    "You prep an AE for a live call. Read call notes, past proposals, and "
    f"product references from path_part_id={CORPUS}. Be concrete and cite "
    "real chunk_ids from read output. Never invent dollar figures or names."
)


async def run(account: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=AccountBrief)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Account: {account}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--account", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.account))


if __name__ == "__main__":
    main()
