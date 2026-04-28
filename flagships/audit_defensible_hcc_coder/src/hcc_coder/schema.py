"""Structured output for the audit-defensible HCC coder."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class CodeAssignment(BaseModel):
    code: str = Field(..., description="ICD-10-CM code, e.g. E11.22")
    description: str = Field(..., max_length=240)
    hcc_category: str | None = Field(
        default=None,
        description="CMS-HCC v24/v28 category if code maps to an HCC; else null.",
    )
    supporting_phrase: str = Field(
        ...,
        max_length=400,
        description="The exact clinical phrase that justifies the code, copied verbatim.",
    )
    encounter_date: str = Field(..., description="YYYY-MM-DD of the DOS that supports the code.")
    confidence: str = Field(..., pattern="^(low|medium|high)$")
    citations: list[Citation] = Field(..., min_length=1, max_length=3)


class UnsupportedFlag(BaseModel):
    claim_code: str
    reason: str = Field(..., max_length=400)


class CoderReport(BaseModel):
    patient_id: str
    assignments: list[CodeAssignment] = Field(..., min_length=1, max_length=40)
    unsupported_flags: list[UnsupportedFlag] = Field(default_factory=list)
    coder_note: str = Field(..., max_length=800)
