"""FNOL structurer — free-text First Notice of Loss → cited structured claim.

Pain point: FNOLs arrive by phone call transcript or email; adjusters re-key
them into the claim system. This recipe extracts a structured claim (party,
loss, coverage questions) from free text, with citations to policy rules.

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

CORPUS = os.environ.get("INSURANCE_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class StructuredFNOL(BaseModel):
    policy_number: str
    insured: str
    loss_date: str
    loss_location: str
    loss_type: str = Field(..., pattern="^(collision|comprehensive|property|liability|workers_comp|other)$")
    parties: list[str] = Field(..., min_length=1, max_length=8)
    description: str = Field(..., max_length=800)
    open_coverage_questions: list[str] = Field(default_factory=list, max_length=6)
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


PROMPT = (
    "You structure FNOLs. Extract policy number, insured, parties, loss type, "
    "and flag coverage questions per our policy-handbook chunks in "
    f"path_part_id={CORPUS}. Never invent policy numbers. chunk_ids must be real."
)


async def run(fnol_file: Path) -> None:
    text = fnol_file.read_text()[:6000]
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=StructuredFNOL)
    async with agent.run_mcp_servers():
        result = await agent.run(f"FNOL free text:\n{text}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fnol-file", type=Path, required=True,
                   help="Free-text file with call transcript or email.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.fnol_file))


if __name__ == "__main__":
    main()
