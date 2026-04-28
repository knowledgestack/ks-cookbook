"""Inbound NDA quick-review against your data-handling and retention policies.

Pain point: Legal/Sales triages every inbound NDA; basic checks (data
classification, retention, sub-processor flow-down, governing law) are
mechanical but get redone each time.

Framework: pydantic-ai with a structured ``NDAReview`` result type.
Tools used: list_contents, read.
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

POLICIES_FOLDER = os.environ.get("POLICIES_FOLDER_ID", "")
class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=300)


class ClauseFlag(BaseModel):
    clause: str = Field(..., description="Short label, e.g. 'Retention'.")
    finding: str = Field(..., description="What's missing or off versus our policy.")
    severity: str = Field(..., pattern="^(low|medium|high)$")
    policy_ref: Citation


class NDAReview(BaseModel):
    counterparty: str
    summary: str = Field(..., max_length=600)
    flags: list[ClauseFlag] = Field(default_factory=list, min_length=1, max_length=12)
    recommendation: str = Field(..., pattern="^(accept|negotiate|reject)$")


PROMPT = """You triage inbound NDAs against the company policies. Use the MCP tools to read
KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs or path_part_id filters in your queries.
2. search_knowledge returns hits. EACH hit is a JSON object with TWO distinct UUIDs: chunk_id (for citation only) and path_part_id (the chunk's path-tree node, used for read). The text field on the hit is empty.
3. To retrieve the chunk content, call read(path_part_id=<hit.path_part_id>). DO NOT pass chunk_id to read — read() returns 404 on chunk_ids. If you see a 404, you used the wrong UUID; switch to path_part_id from the SAME hit. The read() output ends in a [chunk:<uuid>] marker — that uuid is the citation.chunk_id.
4. Build every output field ONLY from chunk text you read. Never invent facts. If the corpus has nothing relevant, mark the field accordingly (e.g. confidence='low' or 'not in corpus — upload data to proceed').
5. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() output's metadata or materialized_path), and snippet (verbatim ≤240 chars from the chunk text). NEVER leave document_name or snippet blank.


Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {"<ClassName>": ...} or {"result": ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""

async def run(counterparty: str, nda_text: str) -> None:
    server_cmd = os.environ.get("KS_MCP_COMMAND", ".venv/bin/ks-mcp")
    server_args = (os.environ.get("KS_MCP_ARGS", "") or "").split()
    mcp = MCPServerStdio(
        command=server_cmd,
        args=server_args,
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o')}",
        mcp_servers=[mcp],
        system_prompt=PROMPT,
        output_type=NDAReview,
        retries=4,
        output_retries=4,
    )
    user_msg = f"Counterparty: {counterparty}\n\nInbound NDA text:\n{nda_text}"
    async with agent.run_mcp_servers():
        result = await agent.run(user_msg)
    print(json.dumps(result.output.model_dump(), indent=2))


SAMPLE_NDA = (
    "1. Confidential Information includes all information disclosed by either party.\n"
    "2. Receiving party shall hold information in confidence indefinitely.\n"
    "3. Receiving party may disclose to affiliates, contractors, and advisors as needed.\n"
    "4. Governed by the laws of the State of Delaware.\n"
)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--counterparty", default="Acme Vendor LLC")
    p.add_argument("--nda-file", help="Path to inbound NDA text file. Default: built-in sample.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    nda_text = Path(args.nda_file).read_text() if args.nda_file else SAMPLE_NDA
    asyncio.run(run(args.counterparty, nda_text))


if __name__ == "__main__":
    main()
