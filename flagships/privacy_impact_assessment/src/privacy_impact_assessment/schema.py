"""Structured output for Privacy Impact Assessment."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class PIAMemo(BaseModel):
    feature_name: str
    data_types_processed: list[str]
    lawful_basis: str
    risks: list[str] = Field(..., min_length=1)
    mitigations: list[str] = Field(..., min_length=1)
    dpo_required: bool
    citations: list[Citation] = Field(..., min_length=1)
