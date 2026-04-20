"""Security awareness quiz — audience → cited 10-question quiz from policy.

Pain point: Annual security training quizzes become stale copy-paste. This
recipe generates a fresh, policy-grounded quiz (MCQ + short answer) with
citations so learners can click through to the source.

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

CORPUS = os.environ.get("SEC_POLICY_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Question(BaseModel):
    prompt: str = Field(..., max_length=300)
    format: str = Field(..., pattern="^(mcq|short)$")
    choices: list[str] = Field(default_factory=list, max_length=5)
    correct: str = Field(..., max_length=200)
    citation: Citation


class Quiz(BaseModel):
    audience: str
    questions: list[Question] = Field(..., min_length=8, max_length=12)


PROMPT = (
    "You write security awareness quizzes. Each question is grounded in a "
    f"specific policy section in path_part_id={CORPUS}. Keep questions "
    "answerable by a non-security employee. chunk_ids must be real."
)


async def run(audience: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=Quiz)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Audience: {audience}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--audience", default="all employees")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.audience))


if __name__ == "__main__":
    main()
