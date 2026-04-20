"""Procurement intake triage — request → cited triage + next-step checklist.

Pain point: Procurement intake forms pile up; IT, security, legal each want
different reviews. This recipe classifies the request and routes it with a
cited checklist of who must review and which policies apply.

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

CORPUS = os.environ.get("PROCUREMENT_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class ReviewStep(BaseModel):
    reviewer: str = Field(..., max_length=80)
    why: str = Field(..., max_length=240)
    sla_days: int = Field(..., ge=0, le=60)
    citation: Citation


class TriageOutcome(BaseModel):
    request_summary: str
    category: str = Field(..., max_length=80)
    data_classification: str = Field(..., pattern="^(public|internal|confidential|restricted)$")
    review_steps: list[ReviewStep] = Field(..., min_length=1, max_length=8)
    estimated_total_days: int = Field(..., ge=1)


PROMPT = (
    "You triage procurement intake requests. Route to security/privacy/legal "
    f"per our procurement + data-classification policies in path_part_id={CORPUS}. "
    "Cite real chunk_ids."
)


async def run(request_summary: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=TriageOutcome)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Request: {request_summary}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--request", required=True, dest="request_summary")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.request_summary))


if __name__ == "__main__":
    main()
