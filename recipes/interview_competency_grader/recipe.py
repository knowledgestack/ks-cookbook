"""Interview competency grader — transcript + rubric → cited per-competency grade.

Pain point: Interviewers rate on instinct. This recipe reads the transcript,
scores against the competency rubric in your corpus, and cites concrete
moments in the transcript that support each rating.

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


class CompetencyGrade(BaseModel):
    competency: str = Field(..., max_length=120)
    rating: str = Field(..., pattern="^(below|meets|exceeds)$")
    rubric_definition_cited: Citation
    transcript_evidence: str = Field(..., max_length=400)


class InterviewGrade(BaseModel):
    role: str
    candidate: str
    hire_recommendation: str = Field(..., pattern="^(strong_hire|hire|no_hire|strong_no_hire)$")
    competencies: list[CompetencyGrade] = Field(..., min_length=3, max_length=8)
    notes: str = Field(..., max_length=600)


PROMPT = (
    "You grade interview transcripts against the rubric in "
    f"path_part_id={CORPUS}. Every rating cites the rubric chunk_id plus the "
    "specific transcript moment. No vibes-based ratings."
)


async def run(role: str, candidate: str, transcript_file: Path) -> None:
    text = transcript_file.read_text()[:10000]
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=InterviewGrade)
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Role: {role}\nCandidate: {candidate}\n\nTranscript:\n{text}"
        )
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--role", required=True)
    p.add_argument("--candidate", required=True)
    p.add_argument("--transcript-file", type=Path, required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.role, args.candidate, args.transcript_file))


if __name__ == "__main__":
    main()
