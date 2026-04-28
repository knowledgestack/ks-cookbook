"""VC due-diligence memo — company + data room → cited IC memo.

Pain point: a VC associate spends a week turning a data room into a
partner-ready investment-committee memo (team / market / product / traction
/ competition / terms / risks). This recipe reads the data room from KS
and emits the structured memo with citations for every fact.

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

class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Finding(BaseModel):
    claim: str = Field(..., max_length=400)
    citation: Citation


class Risk(BaseModel):
    risk: str = Field(..., max_length=300)
    severity: str = Field(..., pattern="^(low|medium|high|deal_breaker)$")
    citation: Citation


class DiligenceMemo(BaseModel):
    company: str
    round_: str = Field(..., alias="round", max_length=40)
    recommendation: str = Field(..., pattern="^(pass|track|diligence_deeper|ic_yes)$")
    tl_dr: str = Field(..., max_length=600)
    team: list[Finding] = Field(..., min_length=1, max_length=6)
    market: list[Finding] = Field(..., min_length=1, max_length=6)
    product: list[Finding] = Field(..., min_length=1, max_length=6)
    traction: list[Finding] = Field(..., min_length=1, max_length=6)
    competition: list[Finding] = Field(default_factory=list, max_length=6)
    terms_and_structure: list[Finding] = Field(default_factory=list, max_length=6)
    risks: list[Risk] = Field(..., min_length=1, max_length=10)

    class Config:
        populate_by_name = True


PROMPT = """You are a VC associate drafting an IC memo. Read the data room in
KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs or path_part_id filters in your queries.
2. search_knowledge returns hits. EACH hit is a JSON object with TWO distinct UUIDs: chunk_id (for citation only) and path_part_id (the chunk's path-tree node, used for read). The text field on the hit is empty.
3. To retrieve the chunk content, call read(path_part_id=<hit.path_part_id>). DO NOT pass chunk_id to read — read() returns 404 on chunk_ids. If you see a 404, you used the wrong UUID; switch to path_part_id from the SAME hit. The read() output ends in a [chunk:<uuid>] marker — that uuid is the citation.chunk_id.
4. Build every output field ONLY from chunk text you read. Never invent facts. If the corpus has nothing relevant, mark the field accordingly (e.g. confidence='low' or 'not in corpus — upload data to proceed').
5. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() output's metadata or materialized_path), and snippet (verbatim ≤240 chars from the chunk text). NEVER leave document_name or snippet blank.


Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {"<ClassName>": ...} or {"result": ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""

async def run(company: str, round_: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", ".venv/bin/ks-mcp"),
        args=(os.environ.get("KS_MCP_ARGS", "") or "").split(),
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o')}",
        mcp_servers=[mcp],
        system_prompt=PROMPT,
        output_type=DiligenceMemo,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(f"Company: {company}. Round: {round_}.")
    print(json.dumps(result.output.model_dump(by_alias=True), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--company", required=True)
    p.add_argument("--round", dest="round_", required=True, help="e.g. 'Seed', 'Series A'")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.company, args.round_))


if __name__ == "__main__":
    main()
