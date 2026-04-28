# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportAny=false, reportAttributeAccessIssue=false, reportUnusedCallResult=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportOptionalSubscript=false, reportReturnType=false, reportMissingTypeArgument=false, reportDeprecated=false, reportUnannotatedClassAttribute=false
"""Cash-flow anomaly detector — bank CSV path → cited anomaly list.

Pain point: Controllers reconcile bank statements line by line and miss
unusual patterns (duplicate vendors, weekend ACH bursts, above-threshold
cash withdrawals). This recipe scans the CSV for anomalies and asks
Knowledge Stack about your AP/AR notes + expense / treasury policy to
ground each suggested control in real chunks of those documents.

Framework: pydantic-ai. KS access via the knowledgestack-mcp stdio server.
Output: stdout (JSON).
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class Anomaly(BaseModel):
    pattern: str = Field(..., max_length=160)
    example_lines: list[str] = Field(..., min_length=1, max_length=5)
    severity: str = Field(..., pattern="^(info|low|medium|high)$")
    suggested_control: str = Field(..., max_length=300)
    citations: list[Citation] = Field(..., min_length=1, max_length=3)


class AnomalyReport(BaseModel):
    source_csv: str
    anomalies: list[Anomaly] = Field(..., min_length=1, max_length=15)


PROMPT = (
    "You're a controller reviewing a bank-transaction CSV for anomalies. "
    "Knowledge Stack is your search backend; ask it natural-language "
    "questions about your company's expense policy, treasury controls, "
    "AP/AR notes, and AML thresholds.\n\n"
    "Workflow:\n"
    "1. Scan the CSV in the user message for patterns like:\n"
    "   • duplicate vendor (same vendor name with minor variations like "
    "'Acme LLC' vs 'Acme L.L.C.' billed for the same invoice)\n"
    "   • multiple sub-threshold cash withdrawals on the same/sequential "
    "days (potential structuring)\n"
    "   • weekend / off-hours ACH bursts\n"
    "   • above-policy single-payment thresholds\n"
    "   • new vendor first-payment without onboarding evidence\n"
    "2. For EACH detected pattern, ask Knowledge Stack a specific question, "
    "e.g.:\n"
    "   • 'What is our company's policy on duplicate vendor payments?'\n"
    "   • 'What does FinCEN say about cash structuring under $10,000?'\n"
    "   • 'What is our treasury policy on new-vendor first-payment "
    "approval?'\n"
    "   Frame each query naturally. Never use folder UUIDs or "
    "path_part_id filters.\n"
    "3. search_knowledge returns hits with chunk_id and path_part_id; the "
    "text field is empty. Call read(path_part_id=<hit's path_part_id>) to "
    "get the chunk text. The trailing [chunk:<uuid>] marker is your "
    "citation.chunk_id (NEVER pass chunk_id to read; it 404s).\n"
    "4. Build suggested_control directly from the chunk text. Populate "
    "every citation with chunk_id (from the marker), document_name "
    "(filename in read() output's metadata), and snippet (verbatim ≤240 "
    "chars from the chunk content).\n"
    "5. example_lines: 1–5 verbatim CSV rows that exhibit the pattern."
    """Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""
)
async def run(csv_path: Path) -> None:
    txns = csv_path.read_text()[:8000]
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
        output_type=AnomalyReport,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(f"Source: {csv_path.name}\n\nTransactions:\n{txns}")
    print(json.dumps(result.output.model_dump(), indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv", type=Path, required=True, help="Path to bank transaction CSV.")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.csv))


if __name__ == "__main__":
    main()
