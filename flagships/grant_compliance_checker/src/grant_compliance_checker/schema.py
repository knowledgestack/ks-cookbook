"""Structured output for Grant Compliance Checker."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class ComplianceCheck(BaseModel):
    activity_description: str
    items: list[str] = Field(default_factory=list, description="Each compliance item checked")
    overall_status: str = Field(..., description="COMPLIANT/NON_COMPLIANT/NEEDS_REVIEW")
    citations: list[Citation] = Field(..., min_length=1)
