"""Benefits enrollment Q&A — question → cited answer from SPDs + carrier docs.

Pain point: Open enrollment: employees ask the same 50 questions about HDHP
vs PPO, HSA rules, coverage abroad, dependent age cutoffs. This recipe answers
from your Summary Plan Descriptions with citations.

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


class BenefitsAnswer(BaseModel):
    question: str
    answer: str = Field(..., max_length=1200)
    plan_specific: bool
    contact_for_edge_case: str = Field(..., max_length=200)
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


PROMPT = (
    f"You answer benefits questions from SPDs + carrier docs in "
    f"path_part_id={CORPUS}. If the answer depends on plan tier, say so. "
    "Never quote a number not in the docs. chunk_ids must be real."
)


async def run(question: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=BenefitsAnswer)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Question: {question}")
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
