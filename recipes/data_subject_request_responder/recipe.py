"""Data subject request (DSR) responder — GDPR/CCPA request → cited response plan.

Pain point: A data subject files an access/erasure request. Privacy ops must
confirm the legal basis, pull applicable systems-of-record, quote the relevant
retention/erasure policy, and compose a compliant response.

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

CORPUS = os.environ.get("PRIVACY_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41")


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class DSRResponse(BaseModel):
    request_type: str = Field(..., pattern="^(access|erasure|portability|rectification|objection)$")
    jurisdiction: str = Field(..., max_length=40)
    response_deadline_days: int = Field(..., ge=1, le=90)
    systems_to_query: list[str] = Field(..., min_length=1, max_length=10)
    policy_refs: list[Citation] = Field(..., min_length=1, max_length=6)
    response_draft: str = Field(..., max_length=1600)


PROMPT = (
    "You respond to data subject requests. Determine legal basis, applicable "
    "deadline (GDPR=30d, CCPA=45d), systems to query, and cite our retention "
    f"and privacy policies in path_part_id={CORPUS}. chunk_ids must be real."
)


async def run(request_type: str, jurisdiction: str, subject: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=DSRResponse)
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Type: {request_type}\nJurisdiction: {jurisdiction}\nSubject: {subject}"
        )
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--type", dest="request_type", required=True,
                   choices=["access", "erasure", "portability", "rectification", "objection"])
    p.add_argument("--jurisdiction", default="GDPR")
    p.add_argument("--subject", default="customer (EU, former employee)")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.request_type, args.jurisdiction, args.subject))


if __name__ == "__main__":
    main()
