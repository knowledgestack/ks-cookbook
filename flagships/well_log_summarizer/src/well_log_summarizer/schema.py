"""Structured output every well-log summary must conform to."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class WellEvent(BaseModel):
    event_type: str = Field(..., pattern="^(hse|equipment|formation|lost_time|other)$")
    description: str = Field(..., max_length=600)
    severity: str = Field(..., pattern="^(info|low|medium|high|critical)$")
    citations: list[Citation] = Field(..., min_length=1, max_length=3)


class WellSummary(BaseModel):
    well_id: str
    operator: str = Field(..., max_length=200)
    location: str = Field(..., max_length=200)
    depth_summary: str = Field(..., max_length=400)
    formation_notes: str = Field(..., max_length=800)
    events: list[WellEvent] = Field(..., min_length=1, max_length=20)
    recommended_actions: list[str] = Field(..., min_length=1, max_length=6)
    hse_risk_rating: str = Field(..., pattern="^(low|medium|high|critical)$")
