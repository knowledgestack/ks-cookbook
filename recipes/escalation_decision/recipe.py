"""Escalation decision — ticket summary → cited escalate/hold decision.

Pain point: Frontline agents hesitate between holding and escalating. This
recipe reads the escalation matrix + SLA policy and returns a decision with
the policy citation.

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

CORPUS = os.environ.get("KB_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class EscalationDecision(BaseModel):
    ticket_summary: str
    decision: str = Field(..., pattern="^(hold|escalate_t2|escalate_t3|page_oncall|management_escalation)$")
    reason: str = Field(..., max_length=400)
    who: str = Field(..., max_length=120)
    sla_remaining_minutes: int
    citations: list[Citation] = Field(..., min_length=1, max_length=3)


PROMPT = (
    f"You decide escalations vs the escalation matrix + SLA policy in "
    f"path_part_id={CORPUS}. If SLA remaining < policy threshold, escalate. "
    "If severity high and security/compliance, escalate regardless. chunk_ids "
    "must be real."
)


async def run(summary: str, severity: str, sla_min: int) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=EscalationDecision)
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Summary: {summary}\nSeverity: {severity}\nSLA remaining (min): {sla_min}"
        )
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--summary", required=True)
    p.add_argument("--severity", default="medium")
    p.add_argument("--sla-min", type=int, default=120)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.summary, args.severity, args.sla_min))


if __name__ == "__main__":
    main()
