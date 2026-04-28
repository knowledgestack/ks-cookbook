# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportAny=false, reportAttributeAccessIssue=false, reportUnusedCallResult=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportOptionalSubscript=false, reportReturnType=false, reportMissingTypeArgument=false, reportDeprecated=false, reportUnannotatedClassAttribute=false
"""API deprecation notice — endpoint → cited customer-facing deprecation notice.

Pain point: Deprecations are communicated inconsistently. This recipe asks
Knowledge Stack about your team's deprecation conventions (header format,
minimum notice window, communication template) and your API reference, then
drafts a standard notice with real citations.

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


class DeprecationNotice(BaseModel):
    endpoint: str
    deprecation_reason: str = Field(..., max_length=400)
    replacement: str = Field(..., max_length=200)
    sunset_date: str
    migration_steps: list[str] = Field(..., min_length=2, max_length=8)
    header_to_watch: str = Field(..., max_length=120, description="e.g. Sunset: <date>")
    citations: list[Citation] = Field(..., min_length=1, max_length=4)


PROMPT = (
    "You're an API platform engineer drafting a customer-facing deprecation "
    "notice. Knowledge Stack is your search backend; ask it natural-language "
    "questions about the company's deprecation policy + the affected "
    "endpoint's docs.\n\n"
    "Workflow:\n"
    "1. Ask Knowledge Stack questions like:\n"
    "   • 'What is our minimum deprecation notice window for breaking API "
    "changes?'\n"
    "   • 'What HTTP header signals deprecation in our API responses?'\n"
    "   • 'What does the API reference say about <endpoint>?'\n"
    "   Frame each query naturally. Never use folder UUIDs or "
    "path_part_id filters.\n"
    "2. search_knowledge returns hits with chunk_id and path_part_id; the "
    "text field is empty. Call read(path_part_id=<hit's path_part_id>) to "
    "retrieve the chunk text — the trailing [chunk:<uuid>] marker is your "
    "citation.chunk_id (NEVER pass chunk_id to read; it 404s).\n"
    "3. If the corpus contains general engineering policy (NIST guidance, "
    "AWS Well-Architected, etc.) but no company-specific deprecation "
    "policy, fall back to industry-standard conventions (Sunset header per "
    "RFC 8594, 6-month minimum notice for breaking changes) and cite "
    "whatever policy guidance IS in the corpus.\n"
    "4. Populate every citation with chunk_id (from the marker), "
    "document_name (filename in read() output's metadata), and snippet "
    "(verbatim ≤240 chars from the chunk text).\n"
    "5. migration_steps is a numbered list of concrete actions (≥2)."
    """Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""
)
async def run(endpoint: str, replacement: str, sunset: str) -> None:
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
        output_type=DeprecationNotice,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Endpoint: {endpoint}\nReplacement: {replacement}\nSunset: {sunset}"
        )
    print(json.dumps(result.output.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--endpoint", required=True, help="e.g. POST /v1/ingest")
    p.add_argument("--replacement", required=True, help="e.g. POST /v2/ingest")
    p.add_argument("--sunset", required=True, help="YYYY-MM-DD")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.endpoint, args.replacement, args.sunset))


if __name__ == "__main__":
    main()
