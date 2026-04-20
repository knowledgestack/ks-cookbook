"""Access review — given a user/role/system tuple, judge it against access policies.

Pain point: Quarterly user access reviews are a slog; reviewers don't recall
which policy says "no shared service accounts" or "least privilege for prod".
This recipe: access scenario in → structured judgment with policy citations.

Framework: pydantic-ai with a structured ``AccessReview`` result.
Tools used: list_contents, read.
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

POLICIES_FOLDER = os.environ.get(
    "POLICIES_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41"
)


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=280)


class AccessReview(BaseModel):
    user: str
    system: str
    role: str
    verdict: str = Field(..., pattern="^(approve|revoke|modify)$")
    rationale: str = Field(..., max_length=600)
    findings: list[str] = Field(default_factory=list, min_length=1, max_length=8)
    policy_refs: list[Citation] = Field(default_factory=list, min_length=1)


PROMPT = (
    "You review access grants against the company's access-control and "
    "data-classification policies. Use the MCP tools to read the relevant "
    f"policies from path_part_id={POLICIES_FOLDER}. Choose verdict='revoke' "
    "for any clear violation (shared accounts, prod write without on-call, "
    "non-need-to-know access to restricted data). Cite real chunk_ids in "
    "policy_refs."
)


async def run(user: str, system: str, role: str) -> None:
    server_cmd = os.environ.get("KS_MCP_COMMAND", "uvx")
    server_args = (os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split()
    mcp = MCPServerStdio(
        command=server_cmd, args=server_args,
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
        mcp_servers=[mcp], system_prompt=PROMPT, result_type=AccessReview,
    )
    request = f"User: {user}\nSystem: {system}\nRole/Permission: {role}"
    async with agent.run_mcp_servers():
        result = await agent.run(request)
    print(json.dumps(result.data.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--user", default="contractor-svc-shared",
                   help="User or service account.")
    p.add_argument("--system", default="prod-postgres-primary")
    p.add_argument("--role", default="superuser write")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.user, args.system, args.role))


if __name__ == "__main__":
    main()
