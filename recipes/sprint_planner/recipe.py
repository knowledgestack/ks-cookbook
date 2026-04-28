# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportAny=false, reportAttributeAccessIssue=false, reportUnusedCallResult=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportOptionalSubscript=false, reportReturnType=false, reportMissingTypeArgument=false, reportDeprecated=false, reportUnannotatedClassAttribute=false
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


PROMPT = """You plan sprints. Read the team's backlog, the last sprint's retro, and
KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs or path_part_id filters in your queries.
2. search_knowledge returns hits. EACH hit is a JSON object with TWO distinct UUIDs: chunk_id (for citation only) and path_part_id (the chunk's path-tree node, used for read). The text field on the hit is empty.
3. To retrieve the chunk content, call read(path_part_id=<hit.path_part_id>). DO NOT pass chunk_id to read — read() returns 404 on chunk_ids. If you see a 404, you used the wrong UUID; switch to path_part_id from the SAME hit. The read() output ends in a [chunk:<uuid>] marker — that uuid is the citation.chunk_id.
4. Build every output field ONLY from chunk text you read. Never invent facts. If the corpus has nothing relevant, mark the field accordingly (e.g. confidence='low' or 'not in corpus — upload data to proceed').
5. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() output's metadata or materialized_path), and snippet (verbatim ≤240 chars from the chunk text). NEVER leave document_name or snippet blank.


Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {"<ClassName>": ...} or {"result": ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""

async def run(team: str, sprint: str, capacity_days: int) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", ".venv/bin/ks-mcp"),
        args=(os.environ.get("KS_MCP_ARGS", "") or "").split(),
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o')}",
        mcp_servers=[mcp],
        system_prompt=PROMPT,
        output_type=SprintPlan,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Team: {team}. Sprint: {sprint}. Capacity: {capacity_days} eng-days."
        )
    print(json.dumps(result.output.model_dump(), indent=2))


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
