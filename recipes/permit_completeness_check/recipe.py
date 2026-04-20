"""Permit completeness check — application → cited completeness verdict.

Pain point: Permit intake staff reject applications for missing site plans /
calculations / signatures; applicants resubmit. This recipe reads the
submitted application and checks it against the ordinance's required-items
list, citing the code section.

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

CORPUS = os.environ.get("GOV_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class RequiredItem(BaseModel):
    item: str = Field(..., max_length=200)
    present: bool
    note: str = Field(..., max_length=300)
    citation: Citation


class PermitCheck(BaseModel):
    permit_type: str
    applicant: str
    items: list[RequiredItem] = Field(..., min_length=3, max_length=30)
    decision: str = Field(..., pattern="^(accept|return_for_completeness|reject)$")
    next_step: str = Field(..., max_length=400)


PROMPT = (
    "You check permit applications for completeness against the ordinance's "
    f"required-items list in path_part_id={CORPUS}. Every required item cites "
    "its code section. Never approve a missing item."
)


async def run(permit_type: str, applicant: str, submission_summary: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=PermitCheck)
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Permit type: {permit_type}\nApplicant: {applicant}\n"
            f"Submission summary:\n{submission_summary}"
        )
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--permit-type", required=True, help="e.g. 'residential solar install'")
    p.add_argument("--applicant", required=True)
    p.add_argument("--submission-summary", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.permit_type, args.applicant, args.submission_summary))


if __name__ == "__main__":
    main()
