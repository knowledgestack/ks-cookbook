"""Business continuity drill plan grounded in BCP/DR policies.

Pain point: Annual BCP/DR tabletops need a custom scenario, success criteria,
and references to your real recovery objectives — but they get copy-pasted
from last year and slowly drift from policy.

Framework: pydantic-ai. KS access via the knowledgestack-mcp stdio server.
Output: stdout (JSON) + file (drill-plan.md).
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Inject(BaseModel):
    minute: int = Field(..., ge=0, le=480)
    event: str = Field(..., max_length=300)


class SuccessCriterion(BaseModel):
    criterion: str = Field(..., max_length=240)
    citation: Citation


class DrillPlan(BaseModel):
    scenario: str
    participants: list[str] = Field(..., min_length=2, max_length=12)
    timeline: list[Inject] = Field(..., min_length=5, max_length=8)
    success_criteria: list[SuccessCriterion] = Field(..., min_length=2, max_length=8)
    policy_references: list[Citation] = Field(..., min_length=1, max_length=6)


PROMPT = """You design business continuity / disaster recovery tabletop drills. Knowledge Stack is your search backend; ask it natural-language questions about your BCP/DR, incident response, and RTO/RPO policies.

KS workflow:
1. Ask Knowledge Stack questions like 'What is our RTO/RPO for primary region failover?' or 'Who is on the incident response team?'. Never use folder UUIDs or path_part_id filters.
2. search_knowledge returns hits with chunk_id and path_part_id (text empty). To get content, call read(path_part_id=<hit's path_part_id>). The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read — it 404s.
3. Each success_criterion MUST include a real citation tied to your RTO/RPO/IR policy. policy_references are 1-6 supporting policy chunks.
4. timeline: 5-8 injects with minute (relative to T0) and event description.


Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {"<ClassName>": ...} or {"result": ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""


async def run(scenario: str, out_path: Path) -> None:
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
        output_type=DrillPlan,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(f"Drill scenario: {scenario}")
    plan = result.output
    md = [
        f"# BCP/DR Drill Plan",
        "",
        f"**Scenario:** {plan.scenario}",
        "",
        "## Participants",
        *(f"- {p}" for p in plan.participants),
        "",
        "## Inject Timeline",
        *(f"- T+{i.minute}m — {i.event}" for i in plan.timeline),
        "",
        "## Success Criteria",
        *(
            f"- {c.criterion} [chunk:{c.citation.chunk_id}]"
            for c in plan.success_criteria
        ),
        "",
        "## Policy References",
        *(f"- {p.document_name}: {p.snippet} [chunk:{p.chunk_id}]" for p in plan.policy_references),
    ]
    out_path.write_text("\n".join(md))
    print(json.dumps(plan.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--scenario",
        default="Primary region outage: us-east-1 unavailable for 4 hours.",
    )
    p.add_argument("--out", default="drill-plan.md")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.scenario, Path(args.out)))


if __name__ == "__main__":
    main()
