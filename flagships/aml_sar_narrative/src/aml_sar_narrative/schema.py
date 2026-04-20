"""Structured output every SAR narrative must conform to."""


from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class SARNarrative(BaseModel):
    case_id: str
    subject_name: str = Field(..., max_length=200)
    filing_institution: str = Field(..., max_length=200)
    who: str = Field(..., max_length=600)
    what: str = Field(..., max_length=800)
    when: str = Field(..., max_length=300)
    where: str = Field(..., max_length=300)
    why_suspicious: str = Field(..., max_length=800)
    how: str = Field(..., max_length=800)
    narrative: str = Field(
        ..., max_length=2400,
        description="Full FinCEN-format narrative (≤ ~200 words), flowing prose "
                    "that combines the W/W/W/W/W/H fields.",
    )
    red_flags: list[str] = Field(..., min_length=1, max_length=12)
    citations: list[Citation] = Field(..., min_length=2, max_length=10)
