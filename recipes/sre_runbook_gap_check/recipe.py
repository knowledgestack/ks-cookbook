"""SRE runbook gap check — service → cited gaps vs runbook template.

Pain point: Runbooks exist for some services, not others; quality varies. This
recipe compares an existing service's runbook coverage against your template
(alerts → steps → escalation → rollback) and flags missing sections.

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

CORPUS = os.environ.get("ENG_DOCS_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class SectionStatus(BaseModel):
    section: str = Field(..., max_length=120)
    present: bool
    quality: str = Field(..., pattern="^(missing|weak|adequate|strong)$")
    note: str = Field(..., max_length=300)
    citation: Citation


class GapReport(BaseModel):
    service: str
    sections: list[SectionStatus] = Field(..., min_length=5)
    top_fixes: list[str] = Field(..., min_length=1, max_length=5)


PROMPT = (
    "You audit service runbooks against the template. Sections to check: "
    "alerts, triage steps, escalation path, rollback, known failure modes, "
    "dependencies, observability links. Read the service's runbook and the "
    f"template from path_part_id={CORPUS}. Cite real chunk_ids."
)


async def run(service: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=GapReport)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Service: {service}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--service", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.service))


if __name__ == "__main__":
    main()
