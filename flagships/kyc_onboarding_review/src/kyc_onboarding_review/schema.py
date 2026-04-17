"""Structured output — a KYC onboarding review with checklist and risk tier."""


from enum import Enum

from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    PRESENT = "PRESENT"
    MISSING = "MISSING"
    INCOMPLETE = "INCOMPLETE"


class RiskTier(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    PROHIBITED = "PROHIBITED"


class Citation(BaseModel):
    chunk_id: str = Field(..., description="UUID from a [chunk:<uuid>] marker.")
    document_name: str = Field(..., description="Name of the policy or reg document.")
    quote: str = Field(
        ..., max_length=400,
        description="Verbatim excerpt from the source, <=400 chars.",
    )


class ChecklistItem(BaseModel):
    requirement: str = Field(
        ..., max_length=200,
        description="The specific CDD/KYC requirement being checked.",
    )
    status: DocumentStatus
    evidence_note: str = Field(
        ..., max_length=500,
        description="What evidence is present, what is missing, or why "
        "the item is incomplete.",
    )
    citations: list[Citation] = Field(
        ..., min_length=1, max_length=5,
        description="Policy/regulatory citations supporting this requirement.",
    )


class RiskFactor(BaseModel):
    factor: str = Field(..., max_length=150)
    impact: str = Field(
        ..., max_length=300,
        description="Why this factor affects the risk tier.",
    )
    citations: list[Citation] = Field(default_factory=list, min_length=0, max_length=3)


class KYCReview(BaseModel):
    customer_name: str
    entity_type: str = Field(..., description="e.g. 'LLC', 'Corporation'")
    risk_tier: RiskTier
    risk_tier_rationale: str = Field(
        ..., max_length=600,
        description="Explanation of why this risk tier was assigned.",
    )
    checklist: list[ChecklistItem] = Field(
        ..., min_length=5, max_length=25,
        description="Each CDD requirement checked against submitted docs.",
    )
    risk_factors: list[RiskFactor] = Field(
        ..., min_length=1, max_length=10,
        description="Risk factors identified from the application.",
    )
    edd_required: bool = Field(
        ...,
        description="Whether Enhanced Due Diligence is required before "
        "account opening.",
    )
    pending_items: list[str] = Field(
        default_factory=list,
        description="Items that must be resolved before account can be opened.",
    )
    recommendation: str = Field(
        ..., max_length=400,
        description="Final recommendation: APPROVE / APPROVE WITH CONDITIONS / "
        "DECLINE / ESCALATE TO BSA OFFICER.",
    )
