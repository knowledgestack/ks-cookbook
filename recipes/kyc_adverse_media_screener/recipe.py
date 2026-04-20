"""KYC adverse-media screener — entity name → cited negative-news hits.

Pain point: analysts hand-Google every new counterparty for sanctions,
enforcement, fraud, or reputational news and paste findings into KYC packets.
This recipe runs `search_knowledge` over a seeded negative-news + sanctions
corpus (OFAC SDN, OpenSanctions, DOJ press releases, state enforcement,
curated press), reads top hits, and returns structured flags with citations.

Framework: pydantic-ai. Tools: search_knowledge, read.
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

CORPUS = os.environ.get("KYC_CORPUS_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Hit(BaseModel):
    category: str = Field(
        ...,
        pattern="^(sanctions|enforcement|fraud|litigation|regulatory|reputational|none)$",
    )
    severity: str = Field(..., pattern="^(info|low|medium|high|critical)$")
    summary: str = Field(..., max_length=400)
    citation: Citation


class AdverseMediaReport(BaseModel):
    entity: str
    overall_risk: str = Field(..., pattern="^(clear|monitor|elevated|blocked)$")
    hits: list[Hit] = Field(..., min_length=0, max_length=15)
    analyst_notes: str = Field(..., max_length=600)


PROMPT = (
    "You screen counterparties for adverse media. Run `search_knowledge` with "
    f"the entity name and aliases against folder_id={CORPUS}; then `read` the "
    "top hits. Classify each hit (sanctions / enforcement / fraud / litigation "
    "/ regulatory / reputational) with severity. If nothing surfaces, return "
    "an empty `hits` list and overall_risk='clear'. Every chunk_id MUST be "
    "copied verbatim from a [chunk:<uuid>] marker in the `read` output — never "
    "synthesize."
)


async def run(entity: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
        mcp_servers=[mcp], system_prompt=PROMPT, result_type=AdverseMediaReport,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(f"Entity: {entity}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--entity", required=True, help="Legal entity name to screen.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.entity))


if __name__ == "__main__":
    main()
