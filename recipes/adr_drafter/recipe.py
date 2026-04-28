# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportAny=false, reportAttributeAccessIssue=false, reportUnusedCallResult=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportOptionalSubscript=false, reportReturnType=false, reportMissingTypeArgument=false, reportDeprecated=false, reportUnannotatedClassAttribute=false
"""Architecture Decision Record drafter grounded in security/eng policies.

Pain point: Engineers write ADRs from a blank page; constraint references
(data-classification, encryption, vendor-mgmt) are forgotten until review.
This recipe asks Knowledge Stack about your engineering / security policies
and produces ADR markdown with policy-cited constraints in the "Policy
Constraints" section.

Framework: pydantic-ai. KS access via the knowledgestack-mcp stdio server.
Output: file (adr.md by default).
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio


class PolicyConstraint(BaseModel):
    constraint: str = Field(..., max_length=300)
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class ADR(BaseModel):
    title: str = Field(..., max_length=200)
    status: str = Field(default="Proposed", max_length=40)
    context: str = Field(..., max_length=1200)
    decision: str = Field(..., max_length=600)
    consequences: list[str] = Field(..., min_length=1, max_length=8)
    policy_constraints: list[PolicyConstraint] = Field(..., min_length=1, max_length=8)


PROMPT = """You draft Architecture Decision Records (ADRs). Knowledge Stack is your search backend; ask it natural-language questions about your engineering and security policies (encryption, data classification, vendor management, access control) that constrain the decision.

KS workflow:
1. Ask Knowledge Stack questions like 'What does our security policy say about encryption at rest?' or 'What is our vendor management policy for new dependencies?'. Never use folder UUIDs or path_part_id filters.
2. search_knowledge returns hits with chunk_id and path_part_id (text empty). To get content, call read(path_part_id=<hit's path_part_id>). The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read — it 404s.
3. Build policy_constraints from real chunks. Every PolicyConstraint MUST include chunk_id (verbatim), document_name (filename from read() metadata), snippet (verbatim ≤240 chars).
4. consequences is a 1–8 item bulleted list of expected outcomes / tradeoffs.


Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {"<ClassName>": ...} or {"result": ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""


async def run(decision: str, context: str, out_path: Path) -> None:
    mcp = MCPServerStdio(
        command=os.environ.get("KS_MCP_COMMAND", ".venv/bin/ks-mcp"),
        args=(os.environ.get("KS_MCP_ARGS", "") or "").split(),
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o')}",
        mcp_servers=[mcp],
        system_prompt=PROMPT,
        output_type=ADR,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(f"Decision: {decision}\nContext: {context}")
    adr = result.output
    md = [
        f"# {adr.title}",
        "",
        f"**Status:** {adr.status}",
        "",
        "## Context",
        adr.context,
        "",
        "## Decision",
        adr.decision,
        "",
        "## Consequences",
        *(f"- {c}" for c in adr.consequences),
        "",
        "## Policy Constraints",
        *(
            f"- {c.constraint} [chunk:{c.chunk_id}] — {c.document_name}"
            for c in adr.policy_constraints
        ),
    ]
    out_path.write_text("\n".join(md))
    # Also print JSON to stdout for the bulk verifier.
    import json as _json
    print(_json.dumps(adr.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--decision",
        default="Adopt managed Postgres for the analytics service",
    )
    p.add_argument(
        "--context",
        default="Current self-hosted Postgres has frequent on-call pages.",
    )
    p.add_argument("--out", default="adr.md")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.decision, args.context, Path(args.out)))


if __name__ == "__main__":
    main()
