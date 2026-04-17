"""Structured output for Incident Runbook Lookup."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class RunbookMatch(BaseModel):
    alert_summary: str
    matched_runbook: str
    severity: str = Field(..., description="P1/P2/P3/P4")
    steps: list[str] = Field(..., min_length=1)
    escalation_path: str
    citations: list[Citation] = Field(..., min_length=1)
