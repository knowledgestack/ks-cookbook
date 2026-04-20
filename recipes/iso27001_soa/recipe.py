"""ISO 27001 SoA drafter — control ID → cited Statement of Applicability entry.

Pain point: Auditors want a clean Statement of Applicability mapping each
Annex A control to applicable/not-applicable + justification + implementation
evidence. This recipe builds the entry with citations from your ISMS docs.

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

CORPUS = os.environ.get("SEC_POLICY_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class SoAEntry(BaseModel):
    control_id: str
    control_title: str = Field(..., max_length=200)
    applicable: bool
    justification: str = Field(..., max_length=400)
    implementation: str = Field(..., max_length=600)
    evidence_refs: list[str] = Field(..., min_length=1, max_length=5)
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


PROMPT = (
    "You draft ISO 27001:2022 SoA entries. Decide applicable/not based on our "
    f"risk register and ISMS docs in path_part_id={CORPUS}. Evidence refs "
    "must point at real documents. chunk_ids must be real."
)


async def run(control_id: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=SoAEntry)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Control: {control_id}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--control-id", required=True, help="e.g. A.8.24")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.control_id))


if __name__ == "__main__":
    main()
