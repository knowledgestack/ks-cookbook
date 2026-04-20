"""Title-defect spotter — recorded-deed text → cited defect list.

Pain point: Title examiners read chains of deeds, mortgages, liens, judgments
and hunt for breaks (missing signatures, wrong legal description, open liens).
This recipe surfaces candidate defects with citations.

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

CORPUS = os.environ.get("REAL_ESTATE_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Defect(BaseModel):
    type: str = Field(..., pattern="^(missing_signature|legal_description|open_lien|chain_break|tax_sale|probate|easement|other)$")
    description: str = Field(..., max_length=500)
    severity: str = Field(..., pattern="^(minor|material|fatal)$")
    curative_action: str = Field(..., max_length=300)
    citation: Citation


class TitleReport(BaseModel):
    parcel: str
    defects: list[Defect] = Field(default_factory=list, max_length=20)
    overall_marketability: str = Field(..., pattern="^(clear|clouded|unmarketable)$")


PROMPT = (
    "You spot title defects from recorded-deed text. Cite the title-examiner "
    f"playbook in path_part_id={CORPUS}. Be conservative — if a finding would "
    "be 'maybe', flag minor, not material. chunk_ids must be real."
)


async def run(parcel: str, chain_file: Path) -> None:
    text = chain_file.read_text()[:10000]
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=TitleReport)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Parcel: {parcel}\n\nChain of title:\n{text}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--parcel", required=True)
    p.add_argument("--chain-file", type=Path, required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.parcel, args.chain_file))


if __name__ == "__main__":
    main()
