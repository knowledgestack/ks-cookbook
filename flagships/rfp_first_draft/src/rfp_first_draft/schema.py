"""Structured output for RFP response drafts."""

from enum import Enum

from pydantic import BaseModel, Field


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Citation(BaseModel):
    chunk_id: str = Field(
        ..., description="UUID copied verbatim from a [chunk:<uuid>] marker."
    )
    source_document: str = Field(
        ..., max_length=200, description="Name of the source proposal/document."
    )
    quote: str = Field(
        ...,
        max_length=400,
        description="Verbatim excerpt from the source, <=400 chars.",
    )


class QuestionResponse(BaseModel):
    question: str = Field(
        ..., max_length=500, description="The RFP question being answered."
    )
    answer: str = Field(
        ...,
        max_length=2000,
        description="Draft response grounded in past proposals.",
    )
    confidence: Confidence = Field(
        ..., description="How well the answer is supported by existing collateral."
    )
    citations: list[Citation] = Field(
        ...,
        min_length=1,
        max_length=8,
        description="Citations to past proposals backing this answer.",
    )


class RFPDraft(BaseModel):
    rfp_title: str = Field(
        ..., max_length=200, description="Title or short description of the RFP."
    )
    responses: list[QuestionResponse] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="One entry per RFP question addressed.",
    )
    overall_notes: str = Field(
        default="",
        max_length=500,
        description="Any caveats, gaps, or areas needing SME review.",
    )
