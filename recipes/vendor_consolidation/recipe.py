# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportAny=false, reportAttributeAccessIssue=false, reportUnusedCallResult=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportOptionalSubscript=false, reportReturnType=false, reportMissingTypeArgument=false, reportDeprecated=false, reportUnannotatedClassAttribute=false
"""
Vendor consolidation planning agent using Knowledge Stack MCP.

Purpose
-------
Generate a procurement vendor consolidation plan for a category
(e.g. observability, CRM, contact-center) using grounded citations
from contracts, renewal notes, and vendor evaluation material.

Example usage
-------------
python consolidate.py \
  --category observability \
  --save
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_MODEL = "gpt-4o"
DEFAULT_FOLDER_ID = "ab926019-ac7a-579f-bfda-6c52a13c5f41"

MODEL_NAME = os.getenv("MODEL", DEFAULT_MODEL)
FINANCE_FOLDER_ID = os.getenv("FINANCE_FOLDER_ID", DEFAULT_FOLDER_ID)


# ============================================================
# OUTPUT SCHEMA
# ============================================================


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)


class VendorAction(BaseModel):
    vendor: str

    action: str = Field(
        ...,
        pattern="^(keep|migrate|terminate|renegotiate)$",
    )

    rationale: str = Field(..., max_length=400)

    annual_spend: str
    estimated_savings: str

    citation: Citation


class ConsolidationPlan(BaseModel):
    category: str

    vendors: list[VendorAction] = Field(
        ...,
        min_length=2,
    )

    overall_savings_estimate: str

    risks: list[str] = Field(
        default_factory=list,
        max_length=5,
    )


# ============================================================
# SYSTEM PROMPT
# ============================================================


def build_system_prompt(folder_id: str) -> str:
    return f"""
You are a procurement strategy assistant.

Build a vendor consolidation plan using contracts,
renewal notes, SaaS usage reports, and vendor evaluation
documents stored in Knowledge Stack.

Corpus root:
folder_id = {folder_id}


MANDATORY WORKFLOW

1. list_contents(folder_id="{folder_id}")

Locate:
• contracts
• renewal summaries
• SaaS usage reports
• vendor evaluation memos


2. search_knowledge(query=<category>)

Identify overlapping vendors.


3. read(path_part_id=<UUID>)

Extract:

• vendor name
• contract value
• renewal terms
• switching risks
• termination penalties
• unused licenses
• discount opportunities


VERSION RULE

Prefer latest document_version unless older versions
contain pricing absent from newer revisions.


FINANCIAL RULES

Never fabricate:

• dollar values
• renewal dates
• license counts


ACTION RULES

keep → strategic OR lowest cost
migrate → duplicate functionality exists
terminate → unused / redundant vendor
renegotiate → renewal soon OR pricing misaligned


SAVINGS RULE

Savings must be supported by:

• license reduction
• vendor removal
• renegotiation leverage
• price delta


CITATION RULE

Each vendor decision must cite exactly one chunk_id
returned from read()

Never fabricate chunk_ids


OUTPUT FORMAT

Return structured JSON matching schema exactly.
"""


# ============================================================
# MCP AGENT FACTORY
# ============================================================


def build_mcp_server() -> MCPServerStdio:
    """
    Create MCP server connection for Knowledge Stack.
    """

    return MCPServerStdio(
        command=os.getenv("KS_MCP_COMMAND", "uvx"),
        args=os.getenv("KS_MCP_ARGS", "knowledgestack-mcp").split(),
        env={
            "KS_API_KEY": os.getenv("KS_API_KEY", ""),
            "KS_BASE_URL": os.getenv("KS_BASE_URL", ""),
        },
    )


def build_agent() -> Agent:
    """
    Construct agent instance.
    """

    return Agent(
        model=f"openai:{MODEL_NAME}",
        system_prompt=build_system_prompt(FINANCE_FOLDER_ID),
        output_type=ConsolidationPlan,
        retries=4,
        output_retries=4,
        mcp_servers=[build_mcp_server()],
    )


# ============================================================
# EXECUTION PIPELINE
# ============================================================


async def generate_plan(category: str) -> ConsolidationPlan:
    agent = build_agent()

    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Generate consolidation plan for vendor category: {category}"
        )

    return result.output


# ============================================================
# OUTPUT HANDLING
# ============================================================


def persist_plan(plan: ConsolidationPlan) -> Path:
    """
    Save consolidation plan locally.
    """

    filename = (
        f"vendor_consolidation_{plan.category}"
        .lower()
        .replace(" ", "_")
        + ".json"
    )

    path = Path(filename)

    path.write_text(
        json.dumps(plan.model_dump(), indent=2)
    )

    return path


# ============================================================
# ENV VALIDATION
# ============================================================


def validate_env() -> None:
    required = [
        "KS_API_KEY",
        "OPENAI_API_KEY",
    ]

    missing = [key for key in required if not os.getenv(key)]

    if missing:
        sys.exit(
            "Missing required environment variables:\n"
            + "\n".join(missing)
        )


# ============================================================
# CLI
# ============================================================


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "--category",
        required=True,
        help="example: observability, CRM, contact-center",
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="persist output JSON locally",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    validate_env()

    plan = asyncio.run(generate_plan(args.category))

    print(json.dumps(plan.model_dump(), indent=2))

    if args.save:
        saved = persist_plan(plan)
        print(f"\nSaved plan → {saved}")


# ============================================================
# ENTRYPOINT
# ============================================================


if __name__ == "__main__":
    main()
