"""Deal loss retro — closed-lost deal → cited root causes + playbook deltas.

Pain point: Loss reasons in CRM are one-word garbage ("price"). This recipe
reads the real artifacts (call notes, proposal, email thread summary) and
produces a structured retro with citations — what actually happened and which
playbook step failed.

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


class LossRetro(BaseModel):
    deal: str
    lost_to: str = Field(..., max_length=120)
    stated_reason: str = Field(..., max_length=240)
    actual_root_causes: list[str] = Field(..., min_length=1, max_length=6)
    playbook_gaps: list[str] = Field(default_factory=list, max_length=6)
    keep_doing: list[str] = Field(default_factory=list, max_length=4)
    citations: list[Citation] = Field(..., min_length=2, max_length=8)


PROMPT = (
    "You run deal loss retros. Read call notes, proposal docs, and any email "
    f"summaries in path_part_id={CORPUS}. Separate the *stated* reason from "
    "the *actual* root causes. Every root cause and gap cites real chunk_ids."
)


async def run(deal: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=LossRetro)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Lost deal: {deal}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--deal", required=True, help="Deal / opportunity name.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.deal))


if __name__ == "__main__":
    main()
