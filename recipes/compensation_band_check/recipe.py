"""Compensation band check — role + level + location → cited band + verdict.

Pain point: Recruiters ping Total Rewards for every offer: "is $X for Staff SWE
in NYC in band?". This recipe looks up the band doc and returns a cited verdict
with band min / mid / max and any location adjustment.

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

CORPUS = os.environ.get("HR_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class BandCheck(BaseModel):
    role: str
    level: str
    location: str
    band_min: str
    band_mid: str
    band_max: str
    location_adjustment: str = Field(..., max_length=120)
    proposed: str
    verdict: str = Field(..., pattern="^(in_band|above_band|below_band|exception_needed)$")
    rationale: str = Field(..., max_length=400)
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


PROMPT = (
    f"You check comp offers vs bands. Read our comp band doc in "
    f"path_part_id={CORPUS}. Apply location adjustment if defined. Return "
    "verdict + rationale. chunk_ids must be real."
)


async def run(role: str, level: str, location: str, proposed: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=BandCheck)
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Role: {role}\nLevel: {level}\nLocation: {location}\nProposed: {proposed}"
        )
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--role", required=True)
    p.add_argument("--level", required=True)
    p.add_argument("--location", required=True)
    p.add_argument("--proposed", required=True, help="Proposed base salary.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.role, args.level, args.location, args.proposed))


if __name__ == "__main__":
    main()
