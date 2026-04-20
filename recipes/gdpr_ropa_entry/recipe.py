"""GDPR ROPA entry — processing activity → cited Record-of-Processing entry.

Pain point: GDPR Article 30 Records-of-Processing are out-of-date the moment
they're approved. This recipe drafts a ROPA entry (purpose, categories, basis,
transfers, retention) from your data-handling + privacy policy with citations.

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


class ROPAEntry(BaseModel):
    activity: str
    purpose: str = Field(..., max_length=400)
    data_categories: list[str] = Field(..., min_length=1, max_length=10)
    data_subjects: list[str] = Field(..., min_length=1, max_length=6)
    lawful_basis: str = Field(..., pattern="^(consent|contract|legal_obligation|vital_interest|public_task|legitimate_interest)$")
    recipients: list[str] = Field(..., min_length=1, max_length=10)
    international_transfers: str = Field(..., max_length=300)
    retention_period: str = Field(..., max_length=200)
    citations: list[Citation] = Field(..., min_length=2, max_length=6)


PROMPT = (
    f"You draft Article 30 ROPA entries. Read privacy + data-retention + "
    f"subprocessor docs in path_part_id={CORPUS}. Each field cites real "
    "chunk_ids. Never invent a lawful basis."
)


async def run(activity: str) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", "uvx"),
        args=(os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split(),
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
                  mcp_servers=[mcp], system_prompt=PROMPT, result_type=ROPAEntry)
    async with agent.run_mcp_servers():
        result = await agent.run(f"Processing activity: {activity}")
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--activity", required=True,
                   help="e.g. 'customer support ticket handling'")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.activity))


if __name__ == "__main__":
    main()
