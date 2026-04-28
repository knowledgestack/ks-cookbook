# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportAny=false, reportAttributeAccessIssue=false, reportUnusedCallResult=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportOptionalSubscript=false, reportReturnType=false, reportMissingTypeArgument=false, reportDeprecated=false, reportUnannotatedClassAttribute=false
"""AML SAR narrative writer — case → cited FinCEN-format SAR narrative.

Pain point: AML analysts hand-write 200-word Suspicious Activity Report
narratives in FinCEN's Who/What/When/Where/Why/How format. This recipe asks
Knowledge Stack about the case (transaction ledger exports, alert rationale,
KYC notes, FinCEN guidance) and drafts a compliant narrative grounded in
real chunks of those documents.

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


class SARNarrative(BaseModel):
    case_id: str
    who: str = Field(..., max_length=400)
    what: str = Field(..., max_length=600)
    when: str = Field(..., max_length=240)
    where: str = Field(..., max_length=240)
    why_suspicious: str = Field(..., max_length=600)
    how: str = Field(..., max_length=600)
    narrative: str = Field(
        ..., max_length=1600, description="Combined ~200-word narrative paragraph."
    )
    citations: list[Citation] = Field(..., min_length=2, max_length=8)


PROMPT = (
    "You draft AML Suspicious Activity Report (SAR) narratives in FinCEN's "
    "Who/What/When/Where/Why/How format. Knowledge Stack is your search "
    "backend; you ask natural-language questions about the case and "
    "FinCEN guidance.\n\n"
    "Workflow:\n"
    "1. Ask Knowledge Stack about the case and the SAR conventions, e.g.:\n"
    "   • 'Summarize the transaction pattern for case <case_id>.'\n"
    "   • 'What FinCEN guidance describes structuring or layering "
    "indicators in SAR narratives?'\n"
    "   • 'What KYC details are on file for the subject of case "
    "<case_id>?'\n"
    "   Frame it the way an AML analyst would ask a colleague. Never use "
    "folder UUIDs or path_part_id filters.\n"
    "2. search_knowledge returns hits with chunk_id and path_part_id; the "
    "text field is empty. Call read(path_part_id=<hit's path_part_id>) to "
    "retrieve the chunk text. The trailing [chunk:<uuid>] marker is the "
    "citation.chunk_id (NEVER pass chunk_id to read — it 404s).\n"
    "3. Build each WWWWWH field ONLY from the chunk text you read. If the "
    "corpus does NOT contain a case file matching the case_id (e.g. only "
    "FinCEN guidance is available), set the field to "
    "'NOT IN CORPUS — upload case file to proceed' rather than inventing "
    "names, amounts, or dates. Never fabricate. Combined narrative ≤ ~200 "
    "words.\n"
    "4. Populate every citation with chunk_id (from the marker), "
    "document_name (filename in the read() output's metadata), and "
    "snippet (verbatim ≤240 chars from the chunk text)."
    """Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""
)
async def run(case_id: str) -> None:
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
        output_type=SARNarrative,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(f"AML case: {case_id}")
    print(json.dumps(result.output.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--case-id",
        required=True,
        help="AML case identifier or distinguishing keyword.",
    )
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.case_id))


if __name__ == "__main__":
    main()
