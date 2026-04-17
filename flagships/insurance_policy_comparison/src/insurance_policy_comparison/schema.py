"""Structured output for Insurance Policy Comparison."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class PolicyComparison(BaseModel):
    current_policy: str
    proposed_policy: str
    improvements: list[str] = Field(default_factory=list)
    coverage_gaps: list[str] = Field(default_factory=list)
    premium_change: str
    recommendation: str
    citations: list[Citation] = Field(..., min_length=1)
