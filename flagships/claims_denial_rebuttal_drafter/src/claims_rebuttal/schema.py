"""Structured output for the claims denial rebuttal."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class CoverageCriterion(BaseModel):
    criterion: str = Field(..., max_length=400)
    policy_citation: Citation
    supporting_evidence: list[Citation] = Field(..., min_length=1, max_length=4)
    is_met: bool


class RebuttalLetter(BaseModel):
    patient_id: str
    denial_code: str
    payer: str
    service_in_question: str = Field(..., max_length=200)
    opening_paragraph: str = Field(..., max_length=800)
    criteria: list[CoverageCriterion] = Field(..., min_length=1, max_length=10)
    closing_paragraph: str = Field(..., max_length=600)
    requested_action: str = Field(..., max_length=300)
