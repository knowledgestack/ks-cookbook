"""Sprint planner — backlog + capacity → cited draft sprint plan.

Pain point: every sprint planning meeting re-debates priority, capacity,
and carry-over from scratch because nobody re-reads the last retros. This
recipe pulls the backlog + last-sprint retro + planning policy from KS,
and emits an ordered plan with size/owner hints and risk callouts. Every
line carries a citation.

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

CORPUS = os.environ.get("ENG_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class PlannedItem(BaseModel):
    rank: int = Field(..., ge=1, le=50)
    title: str = Field(..., max_length=200)
    size: str = Field(..., pattern="^(XS|S|M|L|XL)$")
    owner_hint: str = Field(..., max_length=80, description="Name or '<unassigned>'.")
    rationale: str = Field(..., max_length=300)
    citation: Citation


class SprintPlan(BaseModel):
    team: str
    sprint: str
    capacity_days: int = Field(..., ge=1, le=200)
    committed_items: list[PlannedItem] = Field(..., min_length=1, max_length=20)
    stretch_items: list[PlannedItem] = Field(default_factory=list, max_length=10)
    carryover_from_last_sprint: list[str] = Field(default_factory=list, max_length=15)
    risks: list[str] = Field(default_factory=list, max_length=8)
    retro_themes_addressed: list[str] = Field(default_factory=list, max_length=8)


PROMPT = (
    "You plan sprints. Read the team's backlog, the last sprint's retro, and "
    f"any planning policy in folder_id={CORPUS}. Rank committed items to fit "
    "capacity; mark the rest as stretch. Explicitly address themes from the "
    "last retro. Owner hints only when the source names a person. chunk_ids "
    "MUST be copied verbatim from [chunk:<uuid>] markers in read output."
)


async def run(team: str, sprint: str, capacity_days: int) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=SprintPlan)
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Team: {team}. Sprint: {sprint}. Capacity: {capacity_days} eng-days."
        )
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--team", required=True)
    p.add_argument("--sprint", required=True, help="Sprint identifier, e.g. 2026-S08.")
    p.add_argument("--capacity-days", type=int, required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.team, args.sprint, args.capacity_days))


if __name__ == "__main__":
    main()
