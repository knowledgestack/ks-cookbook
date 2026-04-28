"""Output schema the agent must produce for each questionnaire row."""

from enum import Enum

from pydantic import BaseModel, Field


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Citation(BaseModel):
    chunk_id: str = Field(..., description="UUID of the supporting chunk in KS.")
    document_name: str = Field(..., description="Human-readable policy name.")
    snippet: str = Field(..., max_length=400, description="The cited text.")


class AnsweredControl(BaseModel):
    answer: str = Field(
        ...,
        max_length=20,
        description=(
            "Yes | No | N/A | Partial | INSUFFICIENT EVIDENCE — "
            "use INSUFFICIENT EVIDENCE when retrieved context can't ground the answer."
        ),
    )
    description: str = Field(
        ...,
        max_length=2000,
        description="Short auditor-style narrative. Cites policy sections inline.",
    )
    confidence: Confidence
    citations: list[Citation] = Field(
        default_factory=list,
        description="Must be non-empty unless confidence=LOW + answer=INSUFFICIENT EVIDENCE.",
    )
