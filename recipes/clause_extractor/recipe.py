"""Clause extractor — contract name → cited inventory of standard clauses.

Pain point: Legal ops needs to know "does this MSA have a limitation of
liability cap? indemnity? IP assignment? auto-renew?" across hundreds of
contracts. This recipe produces a cited clause inventory per document.

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

CORPUS = os.environ.get(
    "LEGAL_CORPUS_FOLDER_ID", "5fa0e0af-561c-5e4e-bfa3-2b66d0e40feb"
)

CLAUSES = [
    "limitation of liability", "indemnification", "IP assignment",
    "auto-renewal", "termination for convenience", "governing law",
    "confidentiality", "data processing", "warranty disclaimer",
    "force majeure", "assignment", "notices",
]


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class ClauseHit(BaseModel):
    clause: str
    present: bool
    excerpt: str = Field(..., max_length=400)
    citation: Citation


class ClauseInventory(BaseModel):
    contract: str
    clauses: list[ClauseHit] = Field(..., min_length=3)


PROMPT = (
    f"You inventory contract clauses. For each of these clauses: {CLAUSES}, "
    "report present=true/false, quote the exact excerpt, and cite the real "
    f"chunk_id. Corpus: path_part_id={CORPUS}."
)


async def run(contract: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=ClauseInventory)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Contract: {contract}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--contract", required=True, help="Contract name or keyword.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.contract))


if __name__ == "__main__":
    main()
