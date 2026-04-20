"""Prospecting email personalizer — persona + account → cited cold email.

Pain point: Personalization at scale is fake personalization. This recipe
grounds each hook in something we actually know (past interaction, public
signal notes, case study that matches the vertical) with chunk citations.

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

CORPUS = os.environ.get("SALES_NOTES_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Email(BaseModel):
    subject: str = Field(..., max_length=80)
    body: str = Field(..., max_length=1200)
    personalization_hook: str = Field(..., max_length=200)
    cta: str = Field(..., max_length=160)
    citations: list[Citation] = Field(..., min_length=1, max_length=3)


PROMPT = (
    "You write B2B cold emails. Use ONE concrete personalization hook grounded "
    f"in path_part_id={CORPUS} (past interaction, case study, account note). "
    "No generic flattery. Under 140 words. Citations must be real chunk_ids."
)


async def run(persona: str, account: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=Email)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Persona: {persona}\nAccount: {account}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--persona", required=True, help="e.g. VP Engineering")
    p.add_argument("--account", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.persona, args.account))


if __name__ == "__main__":
    main()
