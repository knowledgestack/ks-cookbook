"""Security finding triage — scanner finding → cited triage verdict.

Pain point: SAST/DAST/SCA drop hundreds of findings. Security engineers
re-triage noise. This recipe classifies a finding (true/likely/false positive),
maps it to policy/exception rules, and produces a cited verdict.

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


class TriageVerdict(BaseModel):
    finding_id: str
    classification: str = Field(..., pattern="^(true_positive|likely_true|false_positive|needs_more_info)$")
    severity: str = Field(..., pattern="^(info|low|medium|high|critical)$")
    policy_exception_applies: bool
    remediation: str = Field(..., max_length=500)
    sla_days: int = Field(..., ge=0, le=365)
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


PROMPT = (
    "You triage security findings. Match finding to our severity rubric, "
    f"exception policy, and remediation SLAs in path_part_id={CORPUS}. Be "
    "concrete. chunk_ids must be real."
)


async def run(finding_id: str, description: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=TriageVerdict)
    async with agent.run_mcp_servers():
        result = await agent.run(f"ID: {finding_id}\nDescription: {description}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--id", dest="finding_id", required=True)
    p.add_argument("--description", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.finding_id, args.description))


if __name__ == "__main__":
    main()
