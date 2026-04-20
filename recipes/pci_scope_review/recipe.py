"""PCI scope review — system → cited in-scope / out-of-scope determination.

Pain point: PCI DSS scope debates eat hours before every audit. This recipe
reads your CDE diagram + data-flow doc and returns a cited classification
(in-scope, connected, out-of-scope) with the controls that apply.

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


class PCIClassification(BaseModel):
    system: str
    scope: str = Field(..., pattern="^(in_scope|connected_to|out_of_scope)$")
    rationale: str = Field(..., max_length=500)
    applicable_controls: list[str] = Field(..., min_length=1, max_length=12)
    compensating_controls: list[str] = Field(default_factory=list, max_length=6)
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


PROMPT = (
    "You classify systems for PCI DSS v4 scope. A system is in-scope if it "
    "stores/processes/transmits CHD, connected if it can impact the CDE. "
    f"Read the CDE diagram + data-flow doc in path_part_id={CORPUS}. "
    "Cite real chunk_ids."
)


async def run(system: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=PCIClassification)
    async with agent.run_mcp_servers():
        result = await agent.run(f"System: {system}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--system", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.system))


if __name__ == "__main__":
    main()
