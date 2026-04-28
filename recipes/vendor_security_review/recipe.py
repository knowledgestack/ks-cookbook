# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportAny=false, reportAttributeAccessIssue=false, reportUnusedCallResult=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportOptionalSubscript=false, reportReturnType=false, reportMissingTypeArgument=false, reportDeprecated=false, reportUnannotatedClassAttribute=false
"""Vendor security review — vendor name + category → cited risk memo.

Pain point: Every new vendor kicks off a 3rd-party risk review. Security
teams want a consistent first draft grounded in the company's vendor-mgmt,
breach-response, and data-protection policies.

Framework: pydantic-ai. KS access via the knowledgestack-mcp stdio server.
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


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class RiskItem(BaseModel):
    risk: str = Field(..., max_length=240)
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    mitigation: str = Field(..., max_length=300)
    citation: Citation


class VendorReview(BaseModel):
    vendor: str
    category: str
    risks: list[RiskItem] = Field(..., min_length=3, max_length=5)
    recommendation: str = Field(..., pattern="^(approve|conditional|reject)$")
    rationale: str = Field(..., max_length=400)


PROMPT = """Available MCP tools (use ONLY these): search_knowledge, search_keyword, read, find, list_contents, get_info. There is NO 'cite' tool. You're a security analyst drafting a first-pass vendor-risk memo. Knowledge Stack is your search backend; ask it natural-language questions about the company's vendor-management, breach-response, and data-protection policies.

KS workflow:
1. Ask Knowledge Stack questions like 'What does our vendor management policy require for sub-processors?' or 'What is our breach notification timeline?'. Never use folder UUIDs or path_part_id filters.
2. search_knowledge returns hits with chunk_id and path_part_id (text empty). To get content, call read(path_part_id=<hit's path_part_id>). The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read — it 404s.
3. Build 3-5 RiskItems each grounded in a real policy chunk. recommendation is approve/conditional/reject based on the risk profile.


Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {"<ClassName>": ...} or {"result": ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""


async def run(vendor: str, category: str) -> None:
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
        output_type=VendorReview,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(f"Vendor: {vendor}\nCategory: {category}")
    print(json.dumps(result.output.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vendor", required=True, help="Vendor company name.")
    p.add_argument("--category", default="data processor", help="e.g. data processor, payment processor, hosting.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.vendor, args.category))


if __name__ == "__main__":
    main()
