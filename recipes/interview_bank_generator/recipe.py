"""Interview bank generator — role → cited interview question set per competency.

Pain point: Hiring managers improvise interview questions. This recipe pulls
competencies from the role's JD/leveling doc and returns a structured question
bank (behavioral + technical + case) with citations.

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


class CompetencyQuestions(BaseModel):
    competency: str = Field(..., max_length=120)
    behavioral: list[str] = Field(..., min_length=2, max_length=5)
    technical_or_case: list[str] = Field(..., min_length=1, max_length=4)
    what_good_looks_like: str = Field(..., max_length=400)
    citation: Citation


class QuestionBank(BaseModel):
    role: str
    level: str = Field(..., max_length=40)
    competencies: list[CompetencyQuestions] = Field(..., min_length=3, max_length=8)


PROMPT = (
    f"You build an interview bank. Read the role's JD and leveling rubric in "
    f"path_part_id={CORPUS}. Produce per-competency behavioral + technical/case "
    "questions and a 'what good looks like' blurb. chunk_ids must be real."
)


async def run(role: str, level: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=QuestionBank)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Role: {role}\nLevel: {level}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--role", required=True)
    p.add_argument("--level", default="Senior")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.role, args.level))


if __name__ == "__main__":
    main()
