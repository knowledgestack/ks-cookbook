"""Structured output for the SMB invoice follow-up agent."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class ToneSample(BaseModel):
    observation: str = Field(..., max_length=400)
    citation: Citation


class FollowUpDraft(BaseModel):
    client: str
    invoice_number: str
    days_overdue: int = Field(..., ge=0)
    tone_analysis: list[ToneSample] = Field(..., min_length=1, max_length=4)
    subject: str = Field(..., max_length=140)
    body: str = Field(..., max_length=2000)
    suggested_send_hour_local: int = Field(..., ge=0, le=23)
    evidence: list[Citation] = Field(default_factory=list)
