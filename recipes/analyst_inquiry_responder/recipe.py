"""Analyst inquiry responder — analyst question → cited talking points.

Pain point: Gartner / Forrester / IDC inquiries come with precise questions;
you have 30 minutes to prep. This recipe builds a talking-point sheet with
cited evidence from product docs, case studies, and customer proof.

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

CORPUS = os.environ.get("MARKETING_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class AnalystPrep(BaseModel):
    analyst_question: str
    headline_answer: str = Field(..., max_length=400)
    talking_points: list[str] = Field(..., min_length=2, max_length=5)
    proof_points: list[str] = Field(..., min_length=2, max_length=5)
    anticipated_followups: list[str] = Field(..., min_length=2, max_length=4)
    citations: list[Citation] = Field(..., min_length=2, max_length=6)


PROMPT = (
    f"You prep an exec for an analyst inquiry. Draw every claim from "
    f"path_part_id={CORPUS} — product docs, case studies, customer proof. "
    "chunk_ids must be real. No hand-wavy answers."
)


async def run(question: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=AnalystPrep)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Analyst question: {question}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--question", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.question))


if __name__ == "__main__":
    main()
