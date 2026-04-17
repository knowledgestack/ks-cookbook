"""Structured output — a covenant compliance report."""


from enum import Enum

from pydantic import BaseModel, Field


class ComplianceStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    WARNING = "WARNING"
    BREACH = "BREACH"


class Citation(BaseModel):
    chunk_id: str = Field(..., description="UUID from a [chunk:<uuid>] marker.")
    document_name: str = Field(..., description="Name of the source document.")
    quote: str = Field(
        ..., max_length=400,
        description="Verbatim excerpt from the document, <=400 chars.",
    )


class CovenantCheck(BaseModel):
    covenant_name: str = Field(
        ..., max_length=120,
        description="e.g. 'Maximum Consolidated Leverage Ratio'",
    )
    required_threshold: str = Field(
        ..., max_length=80,
        description="e.g. '4.00 to 1.00' or '>= 3.00x'",
    )
    actual_value: str = Field(
        ..., max_length=80,
        description="e.g. '1.89x' or '$27,450K'",
    )
    status: ComplianceStatus
    analysis: str = Field(
        ..., max_length=800,
        description="Explanation of how actual compares to threshold, any "
        "headroom or shortfall, and materiality.",
    )
    cure_rights: str = Field(
        default="",
        max_length=400,
        description="Available cure mechanisms, if any.",
    )
    citations: list[Citation] = Field(..., min_length=1, max_length=5)


REPORT_TEMPLATE = """\
# Covenant Compliance Report

**Borrower:** {borrower}
**Period:** {period}
**Report Date:** {report_date}
**Overall Status:** {overall_status}

## Executive Summary
{executive_summary}

## Covenant-by-Covenant Analysis
{covenant_sections}

## Recommended Actions
{recommended_actions}

## Citations
{citation_list}
"""
