"""Structured output every RFI draft must conform to."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class SpecReference(BaseModel):
    csi_division: str = Field(..., max_length=20, description="e.g. '23 05 93'")
    section_title: str = Field(..., max_length=160)
    citation: Citation


class RFIDraft(BaseModel):
    rfi_number: str
    subject: str = Field(..., max_length=240)
    question_restatement: str = Field(..., max_length=600)
    draft_response: str = Field(..., max_length=1800)
    spec_references: list[SpecReference] = Field(..., min_length=1, max_length=5)
    drawing_references: list[str] = Field(
        default_factory=list,
        description="Sheet numbers or detail tags referenced in the response.",
    )
    schedule_impact_days: int = Field(..., ge=0, le=365)
    cost_impact: str = Field(..., max_length=240, description="'none' or a budgeted range.")
    needs_architect_response: bool = Field(
        ...,
        description="True if the question implicates design intent and requires AoR sign-off.",
    )
    confidence: str = Field(..., pattern="^(low|medium|high)$")
    citations: list[Citation] = Field(..., min_length=1, max_length=8)
