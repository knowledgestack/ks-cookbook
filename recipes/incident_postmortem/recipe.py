"""Incident post-mortem drafter grounded in the IR / breach policies.

Pain point: SREs write post-mortems from scratch each incident; format drifts,
policy references get stale.  This recipe: incident summary → a post-mortem
with timeline, root cause, remediation, and cited policy references.

Framework: pydantic-ai with a structured ``PostMortem`` result type.
"""


import argparse
import asyncio
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

POLICIES_FOLDER = os.environ.get(
    "POLICIES_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41"
)


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=300)


class PostMortem(BaseModel):
    title: str
    summary: str = Field(..., max_length=1000)
    timeline: list[str] = Field(default_factory=list, min_length=3, max_length=20)
    root_cause: str
    remediation: list[str] = Field(default_factory=list, min_length=1, max_length=10)
    policy_references: list[Citation] = Field(default_factory=list, min_length=1)


PROMPT = (
    "You draft engineering post-mortems. Use the MCP tools to list and read "
    "the Incident Response (ir) and Breach policies from the folder "
    f"path_part_id={POLICIES_FOLDER}. Cite policy chunks with real chunk_ids "
    "copied from the read output in the ``policy_references`` field."
)


async def run(incident: str) -> None:
    server_cmd = os.environ.get("KS_MCP_COMMAND", "uvx")
    server_args = (os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split()
    mcp = MCPServerStdio(
        command=server_cmd, args=server_args,
        env={"KS_API_KEY": os.environ.get("KS_API_KEY", ""),
             "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o-mini')}",
        mcp_servers=[mcp], system_prompt=PROMPT, result_type=PostMortem,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(incident)
    pm = result.data
    out = Path("post-mortem.md")
    out.write_text(
        f"# {pm.title}\n\n## Summary\n{pm.summary}\n\n"
        f"## Timeline\n" + "\n".join(f"- {t}" for t in pm.timeline) + "\n\n"
        f"## Root cause\n{pm.root_cause}\n\n"
        f"## Remediation\n" + "\n".join(f"- {r}" for r in pm.remediation) + "\n\n"
        "## Policy references\n"
        + "\n".join(
            f"- **{c.document_name}** (chunk:{c.chunk_id}): \u201c{c.snippet}\u201d"
            for c in pm.policy_references
        )
    )
    print(f"Wrote {out}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--incident", required=True,
                   help="One-paragraph summary of the incident.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.incident))


if __name__ == "__main__":
    main()
