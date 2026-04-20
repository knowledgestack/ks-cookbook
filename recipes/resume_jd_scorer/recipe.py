"""Resume-to-JD scorer — resume text + role → cited fit score with bias guards.

Pain point: Recruiters skim 200 resumes per req. This recipe scores fit vs
the JD from your corpus (must-have + nice-to-have), and filters evidence
that is *not* job-relevant (name, age, graduation year, employment gaps) to
reduce bias.

Framework: pydantic-ai. Tools: list_contents, search_knowledge, read.
Output: stdout (JSON).
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

CORPUS = os.environ.get("HR_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class CriterionHit(BaseModel):
    criterion: str = Field(..., max_length=160)
    type: str = Field(..., pattern="^(must_have|nice_to_have)$")
    verdict: str = Field(..., pattern="^(hit|miss|unclear)$")
    evidence_in_resume: str = Field(..., max_length=300)
    citation: Citation


class ResumeScore(BaseModel):
    role: str
    fit_score: int = Field(..., ge=0, le=100)
    criteria: list[CriterionHit] = Field(..., min_length=3, max_length=12)
    non_job_factors_ignored: list[str] = Field(default_factory=list, max_length=6)


PROMPT = (
    "You score resumes vs a JD. Only use job-relevant evidence. Explicitly "
    "ignore name, age, graduation year, employment gaps, photo. JD lives in "
    f"path_part_id={CORPUS}. chunk_ids must be real."
)


async def run(role: str, resume_file: Path) -> None:
    text = resume_file.read_text()[:6000]
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=ResumeScore)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Role: {role}\n\nResume:\n{text}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--role", required=True)
    p.add_argument("--resume-file", type=Path, required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.role, args.resume_file))


if __name__ == "__main__":
    main()
