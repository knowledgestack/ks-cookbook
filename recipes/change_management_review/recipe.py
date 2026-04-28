"""Change management review — proposed change → cited policy-gate checklist.

Pain point: Every PR/deploy that touches prod should map to your change-mgmt
policy (peer review, ticket, rollback plan, off-hours window for risky
changes). Engineers forget the gates; reviewers re-derive them each time.

Framework: pydantic-ai. KS access via the knowledgestack-mcp stdio server.
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


class PolicyGate(BaseModel):
    gate: str = Field(..., max_length=200)
    why: str = Field(..., max_length=240)
    required: bool
    citation: Citation


class ChangeReview(BaseModel):
    change: str
    risk_level: str = Field(..., pattern="^(low|medium|high)$")
    gates: list[PolicyGate] = Field(..., min_length=2, max_length=10)


PROMPT = """You're a change-management reviewer. Knowledge Stack is your search backend; ask it natural-language questions about your change-management / release / deploy / SDLC policies.

KS workflow:
1. Ask Knowledge Stack questions like 'What does our change-management policy require for high-risk database changes?' or 'When is off-hours deploy required?'. Never use folder UUIDs or path_part_id filters.
2. search_knowledge returns hits with chunk_id and path_part_id (text empty). To get content, call read(path_part_id=<hit's path_part_id>). The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read — it 404s.
3. Build 2-10 PolicyGates each tied to a real policy chunk. required=true only if the policy actually requires it for this risk level.


Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {"<ClassName>": ...} or {"result": ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""


async def run(change: str, risk: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o')}",
        mcp_servers=[mcp],
        system_prompt=PROMPT,
        output_type=ChangeReview,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(f"Proposed change: {change}\nRisk level: {risk}")
    print(json.dumps(result.output.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--change",
        default="Drop-and-recreate the orders.user_id index in prod Postgres",
    )
    p.add_argument("--risk", default="high", choices=["low", "medium", "high"])
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.change, args.risk))


if __name__ == "__main__":
    main()
