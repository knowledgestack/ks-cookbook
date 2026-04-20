"""311 citizen-intent router — citizen message → cited department + SLA.

Pain point: 311 call centers triage thousands of messages daily into the right
city department. This recipe classifies intent per your service catalog and
returns owner + SLA + follow-up template with citations.

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

CORPUS = os.environ.get("GOV_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class IntentRoute(BaseModel):
    message: str
    intent_category: str = Field(..., max_length=120)
    department: str = Field(..., max_length=120)
    urgency: str = Field(..., pattern="^(info|normal|urgent|emergency)$")
    sla_hours: int = Field(..., ge=0, le=720)
    followup_template: str = Field(..., max_length=600)
    citation: Citation


PROMPT = (
    "You triage 311 messages per the service catalog in "
    f"path_part_id={CORPUS}. Emergency (life safety) → 911 escalation note. "
    "chunk_ids must be real. Never invent department names."
)


async def run(message: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=IntentRoute)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Citizen message: {message}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--message", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.message))


if __name__ == "__main__":
    main()
