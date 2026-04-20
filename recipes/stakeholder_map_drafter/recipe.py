"""Stakeholder map drafter — account → cited stakeholder map with roles.

Pain point: Deal reviews ask "who is the champion, who's the blocker, who's
the economic buyer?" and AEs guess. This recipe pulls every named person
mentioned in account notes, classifies their role and influence, and cites.

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


class Stakeholder(BaseModel):
    name: str
    title: str = Field(..., max_length=120)
    role: str = Field(..., pattern="^(champion|economic_buyer|user|blocker|influencer|unknown)$")
    sentiment: str = Field(..., pattern="^(advocate|supportive|neutral|skeptical|detractor)$")
    last_touch: str = Field(..., max_length=80)
    citation: Citation


class StakeholderMap(BaseModel):
    account: str
    stakeholders: list[Stakeholder] = Field(..., min_length=1, max_length=20)
    gaps: list[str] = Field(default_factory=list, max_length=5)


PROMPT = (
    f"You build stakeholder maps. Only include people actually named in "
    f"path_part_id={CORPUS}. Never invent a name or title. Gaps = missing "
    "role coverage (e.g. no identified economic buyer). chunk_ids must be real."
)


async def run(account: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=StakeholderMap)
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
