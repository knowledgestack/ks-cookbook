"""Structured output for the SDR session summary."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class MeddicScore(BaseModel):
    metrics: str = Field(..., pattern="^(covered|partial|missing)$")
    economic_buyer: str = Field(..., pattern="^(covered|partial|missing)$")
    decision_criteria: str = Field(..., pattern="^(covered|partial|missing)$")
    decision_process: str = Field(..., pattern="^(covered|partial|missing)$")
    identify_pain: str = Field(..., pattern="^(covered|partial|missing)$")
    champion: str = Field(..., pattern="^(covered|partial|missing)$")


class SessionSummary(BaseModel):
    prospect: str
    turns: int = Field(..., ge=1)
    meddic: MeddicScore
    discovered_pains: list[str] = Field(default_factory=list, max_length=10)
    discovered_metrics: list[str] = Field(default_factory=list, max_length=10)
    next_step: str = Field(..., max_length=400)
    citations_referenced: list[Citation] = Field(default_factory=list, max_length=15)
    open_objections: list[str] = Field(default_factory=list, max_length=10)
