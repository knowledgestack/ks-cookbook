"""Drug-drug interaction checker — medication list → cited interaction report.

Pain point: Pharmacists + clinicians cross-check interactions in DailyMed or
Lexicomp. This recipe runs a structured check against your DailyMed-mirrored
corpus and returns interaction severities with citations.

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

CORPUS = os.environ.get("CLINICAL_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Interaction(BaseModel):
    drug_a: str
    drug_b: str
    severity: str = Field(..., pattern="^(none|monitor|moderate|major|contraindicated)$")
    mechanism: str = Field(..., max_length=400)
    clinical_guidance: str = Field(..., max_length=400)
    citation: Citation


class InteractionReport(BaseModel):
    patient_medications: list[str] = Field(..., min_length=2)
    interactions: list[Interaction] = Field(default_factory=list, max_length=30)
    disclaimer: str = Field(default="Decision-support only; verify with a pharmacist.")


PROMPT = (
    f"You check drug-drug interactions using DailyMed labels in "
    f"path_part_id={CORPUS}. Only report interactions you can cite. No guessing."
)


async def run(meds: list[str]) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=InteractionReport)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Medications: {meds}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--meds", required=True,
                   help="Comma-separated medications, e.g. 'warfarin,amiodarone,simvastatin'")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run([m.strip() for m in args.meds.split(",")]))


if __name__ == "__main__":
    main()
