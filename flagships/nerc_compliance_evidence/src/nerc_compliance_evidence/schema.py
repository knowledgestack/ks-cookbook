"""Structured output for NERC CIP compliance evidence packs."""

from enum import Enum

from pydantic import BaseModel, Field


class EvidenceStatus(str, Enum):
    SATISFIED = "SATISFIED"
    PARTIAL = "PARTIAL"
    GAP = "GAP"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Citation(BaseModel):
    chunk_id: str = Field(
        ..., description="UUID copied verbatim from a [chunk:<uuid>] marker."
    )
    source_document: str = Field(
        ..., max_length=200, description="Name of the source document."
    )
    quote: str = Field(
        ..., max_length=400, description="Verbatim excerpt, <=400 chars."
    )


class EvidenceItem(BaseModel):
    control_description: str = Field(
        ...,
        max_length=300,
        description="What the requirement asks for.",
    )
    status: EvidenceStatus
    evidence_summary: str = Field(
        ...,
        max_length=1000,
        description="Description of the evidence that satisfies (or fails to satisfy) the requirement.",
    )
    citations: list[Citation] = Field(
        ...,
        min_length=1,
        max_length=6,
        description="Citations to procedures/policies backing this evidence.",
    )


class NERCEvidencePack(BaseModel):
    standard_id: str = Field(..., max_length=30, description="e.g. 'CIP-007-6'.")
    requirement: str = Field(..., max_length=20, description="e.g. 'R2'.")
    requirement_text: str = Field(
        ...,
        max_length=1000,
        description="Full text of the NERC CIP requirement.",
    )
    evidence_items: list[EvidenceItem] = Field(
        ...,
        min_length=1,
        max_length=15,
        description="Evidence items mapped to sub-requirements.",
    )
    gaps: list[str] = Field(
        default_factory=list,
        description="Compliance gaps or missing evidence.",
    )
    auditor_notes: str = Field(
        default="",
        max_length=800,
        description="Summary notes for the auditor.",
    )
