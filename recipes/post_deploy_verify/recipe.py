"""Post-deploy verify — service + change → cited post-deploy verification plan.

Pain point: After a deploy, engineers "spot-check" — no checklist. This recipe
produces a concrete verification plan (SLO checks, smoke tests, log patterns,
rollback triggers) grounded in your SRE runbooks.

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

CORPUS = os.environ.get("ENG_DOCS_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Check(BaseModel):
    check: str = Field(..., max_length=200)
    how: str = Field(..., max_length=300)
    red_flag: str = Field(..., max_length=240)


class VerifyPlan(BaseModel):
    service: str
    change: str
    checks: list[Check] = Field(..., min_length=3, max_length=12)
    rollback_triggers: list[str] = Field(..., min_length=1, max_length=6)
    citations: list[Citation] = Field(..., min_length=1, max_length=5)


PROMPT = (
    "You produce post-deploy verification plans. Reference SLOs, dashboards, "
    f"and runbooks in path_part_id={CORPUS}. Red flags must be observable and "
    "actionable. Cite real chunk_ids."
)


async def run(service: str, change: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=VerifyPlan)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Service: {service}\nChange: {change}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--service", required=True)
    p.add_argument("--change", required=True, help="Short description of the deploy.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.service, args.change))


if __name__ == "__main__":
    main()
