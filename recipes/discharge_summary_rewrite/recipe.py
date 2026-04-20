"""Discharge summary plain-language rewrite — clinical summary → patient version.

Pain point: Discharge summaries are dense jargon; AHRQ says patient-friendly
rewrites reduce readmits. This recipe rewrites at ~6th-grade reading level,
preserves every medication and follow-up, and cites the source sentences.

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

CORPUS = os.environ.get("CLINICAL_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class PatientSummary(BaseModel):
    what_happened: str = Field(..., max_length=800)
    your_medications: list[str] = Field(..., min_length=1, max_length=15)
    follow_ups: list[str] = Field(..., min_length=1, max_length=10)
    call_doctor_if: list[str] = Field(..., min_length=2, max_length=8)
    citations: list[Citation] = Field(..., min_length=1, max_length=6)


PROMPT = (
    "You rewrite clinical discharge summaries into patient-friendly language "
    "at ~6th-grade reading level. Preserve every medication and follow-up "
    f"exactly. Ground each section in path_part_id={CORPUS} (original "
    "summary). chunk_ids must be real."
)


async def run(summary_file: Path) -> None:
    text = summary_file.read_text()[:6000]
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=PatientSummary)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Original summary:\n{text}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--summary-file", type=Path, required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.summary_file))


if __name__ == "__main__":
    main()
