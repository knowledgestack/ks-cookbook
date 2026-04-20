"""Inbound lead router — lead form payload → cited segment + owner + next action.

Pain point: Inbound leads land in a big queue; routing is ad-hoc. This recipe
reads the ICP doc + segmentation rules in your corpus and classifies the
lead (SMB / mid-market / enterprise / DQ) with owner + SLA + next action.

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


class LeadRoute(BaseModel):
    company: str
    segment: str = Field(..., pattern="^(smb|mid_market|enterprise|disqualified)$")
    owner_team: str = Field(..., pattern="^(self_serve|sdr|ae_mm|ae_ent|cs)$")
    reply_sla_minutes: int = Field(..., ge=5, le=1440)
    next_action: str = Field(..., max_length=300)
    citations: list[Citation] = Field(..., min_length=1, max_length=3)


PROMPT = (
    f"You route inbound leads per our ICP + segmentation rules in "
    f"path_part_id={CORPUS}. chunk_ids must be real. DQ criteria must be "
    "cited — don't reject a lead on vibes."
)


async def run(payload: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=LeadRoute)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Lead form payload:\n{payload}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--payload", required=True,
                   help="JSON string or plain-text lead payload from the form.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.payload))


if __name__ == "__main__":
    main()
