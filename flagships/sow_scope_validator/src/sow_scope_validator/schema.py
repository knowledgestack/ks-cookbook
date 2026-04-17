"""Structured output for SOW Scope Validator."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class SOWReview(BaseModel):
    project_name: str
    completeness_score: float = Field(..., ge=0, le=1)
    missing_sections: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(..., min_length=1)
