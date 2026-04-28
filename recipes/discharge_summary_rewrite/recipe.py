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


PROMPT = """You rewrite clinical discharge summaries into patient-friendly language
KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs or path_part_id filters in your queries.
2. search_knowledge returns hits. EACH hit is a JSON object with TWO distinct UUIDs: chunk_id (for citation only) and path_part_id (the chunk's path-tree node, used for read). The text field on the hit is empty.
3. To retrieve the chunk content, call read(path_part_id=<hit.path_part_id>). DO NOT pass chunk_id to read — read() returns 404 on chunk_ids. If you see a 404, you used the wrong UUID; switch to path_part_id from the SAME hit. The read() output ends in a [chunk:<uuid>] marker — that uuid is the citation.chunk_id.
4. Build every output field ONLY from chunk text you read. Never invent facts. If the corpus has nothing relevant, mark the field accordingly (e.g. confidence='low' or 'not in corpus — upload data to proceed').
5. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() output's metadata or materialized_path), and snippet (verbatim ≤240 chars from the chunk text). NEVER leave document_name or snippet blank.


Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {"<ClassName>": ...} or {"result": ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""

async def run(summary_file: Path) -> None:
    text = summary_file.read_text()[:6000]
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o')}",
        mcp_servers=[mcp],
        system_prompt=PROMPT,
        output_type=PatientSummary,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(f"Original summary:\n{text}")
    print(json.dumps(result.output.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--summary-file", type=Path, required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.summary_file))


if __name__ == "__main__":
    main()
