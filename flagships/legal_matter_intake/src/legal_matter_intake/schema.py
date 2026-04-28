"""Structured output for the Sertain legal matter intake dossier."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class ConflictHit(BaseModel):
    adverse_party: str
    past_matter: str = Field(..., max_length=300)
    hit_type: str = Field(..., pattern="^(direct|positional|former_client|related_entity|none)$")
    resolution: str = Field(
        ..., description="e.g. 'waiver required', 'decline', 'no action needed'"
    )
    citation: Citation


class RiskFactor(BaseModel):
    title: str = Field(..., max_length=160)
    severity: str = Field(..., pattern="^(low|medium|high|blocker)$")
    narrative: str = Field(..., max_length=600)
    citation: Citation


class FeeEstimate(BaseModel):
    practice_area: str
    staffing_model: str = Field(..., max_length=300)
    low_range: int = Field(..., ge=0)
    high_range: int = Field(..., ge=0)
    currency: str = Field(default="CAD")
    assumptions: str = Field(..., max_length=400)
    citation: Citation


class EthicsDisclosure(BaseModel):
    rule_reference: str
    requirement: str = Field(..., max_length=400)
    citation: Citation


class MatterIntakeDossier(BaseModel):
    client: str
    matter: str = Field(..., max_length=400)
    overall_risk: str = Field(..., pattern="^(low|medium|high|blocker)$")
    conflicts_analysis: list[ConflictHit] = Field(default_factory=list, max_length=10)
    risk_factors: list[RiskFactor] = Field(..., min_length=1, max_length=8)
    fee_estimate: FeeEstimate
    required_disclosures: list[EthicsDisclosure] = Field(..., min_length=1, max_length=6)
    recommended_engagement_terms: list[str] = Field(..., min_length=1, max_length=8)
    partner_notes: str = Field(..., max_length=1000)
