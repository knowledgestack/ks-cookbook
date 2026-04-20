"""9-box performance synthesizer — team → cited 9-box placement per employee.

Pain point: People reviews put every IC on a 9-box (performance × potential).
Managers argue from feelings. This recipe reads the perf docs (retros, peer
feedback, 1:1 notes) and places each person with cited evidence.

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


class NineBoxPlacement(BaseModel):
    employee: str
    performance: str = Field(..., pattern="^(low|meets|high)$")
    potential: str = Field(..., pattern="^(low|growing|high)$")
    placement_label: str = Field(..., max_length=120)
    evidence: str = Field(..., max_length=500)
    development_action: str = Field(..., max_length=300)
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


class NineBoxReport(BaseModel):
    team: str
    placements: list[NineBoxPlacement] = Field(..., min_length=1, max_length=30)


PROMPT = (
    "You place each team member on a 9-box (performance × potential). Ground "
    f"placements in path_part_id={CORPUS} (retros, peer feedback, 1:1 notes). "
    "No placement without citations. chunk_ids must be real."
)


async def run(team: str, employees: list[str]) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=NineBoxReport)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Team: {team}\nEmployees: {employees}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--team", required=True)
    p.add_argument("--employees", required=True, help="Comma-separated names.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.team, [e.strip() for e in args.employees.split(",")]))


if __name__ == "__main__":
    main()
