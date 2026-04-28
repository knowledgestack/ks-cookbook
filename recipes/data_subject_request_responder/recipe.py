# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportAny=false, reportAttributeAccessIssue=false, reportUnusedCallResult=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportOptionalSubscript=false, reportReturnType=false, reportMissingTypeArgument=false, reportDeprecated=false, reportUnannotatedClassAttribute=false
"""Data subject request (DSR) responder — GDPR/CCPA request → cited response plan.

Pain point: A data subject files an access/erasure request. Privacy ops
must confirm the legal basis, pull applicable systems-of-record, quote the
relevant retention/erasure policy, and compose a compliant response. This
recipe asks Knowledge Stack about your privacy policy + retention rules
and grounds every fact in real chunks.

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


class DSRResponse(BaseModel):
    request_type: str = Field(..., pattern="^(access|erasure|portability|rectification|objection)$")
    jurisdiction: str = Field(..., max_length=40)
    response_deadline_days: int = Field(..., ge=1, le=90)
    systems_to_query: list[str] = Field(..., min_length=1, max_length=10)
    policy_refs: list[Citation] = Field(..., min_length=1, max_length=6)
    response_draft: str = Field(..., max_length=1600)


PROMPT = (
    "You're a privacy operations engineer responding to a data subject "
    "request (DSR). Knowledge Stack is your search backend; ask it natural-"
    "language questions about your company's privacy / retention / erasure "
    "policies and the relevant regulation (GDPR, CCPA).\n\n"
    "Workflow:\n"
    "1. Ask Knowledge Stack questions like:\n"
    "   • 'What is the GDPR deadline for an access request?'\n"
    "   • 'What does our retention policy say about erasure of "
    "former-employee data?'\n"
    "   • 'Which systems of record hold customer profile data?'\n"
    "   Frame queries naturally. Never use folder UUIDs or path_part_id "
    "filters.\n"
    "2. search_knowledge returns hits with chunk_id and path_part_id; the "
    "text field is empty. Call read(path_part_id=<hit's path_part_id>) to "
    "get the chunk text. The trailing [chunk:<uuid>] marker is the "
    "citation.chunk_id (NEVER pass chunk_id to read; it 404s).\n"
    "3. Set response_deadline_days from the regulation: GDPR=30, CCPA=45 "
    "(extendable to 60 with notice). Cite the regulation chunk if "
    "available; otherwise cite your privacy policy.\n"
    "4. Populate every policy_ref with chunk_id (verbatim), document_name "
    "(filename in read() metadata), and snippet (verbatim ≤240 chars).\n"
    "5. response_draft is a paragraph the privacy team can send. Quote "
    "policy text verbatim where applicable."
    """Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""
)
async def run(request_type: str, jurisdiction: str, subject: str) -> None:
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
        output_type=DSRResponse,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Type: {request_type}\nJurisdiction: {jurisdiction}\nSubject: {subject}"
        )
    print(json.dumps(result.output.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--type",
        dest="request_type",
        required=True,
        choices=["access", "erasure", "portability", "rectification", "objection"],
    )
    p.add_argument("--jurisdiction", default="GDPR")
    p.add_argument("--subject", default="customer (EU, former employee)")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.request_type, args.jurisdiction, args.subject))


if __name__ == "__main__":
    main()
