"""Structured output every credit memo must conform to."""


from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class RiskFactor(BaseModel):
    title: str = Field(..., max_length=120)
    narrative: str = Field(..., max_length=1200)
    severity: str = Field(..., description="LOW | MEDIUM | HIGH")
    citations: list[Citation] = Field(default_factory=list, min_length=1)


class CovenantRecommendation(BaseModel):
    covenant: str
    rationale: str = Field(..., max_length=500)
    citations: list[Citation] = Field(default_factory=list, min_length=1)


class CreditMemo(BaseModel):
    borrower: str
    facility_summary: str = Field(..., max_length=500)
    recommendation: str = Field(..., description="Approve | Conditional | Decline")
    risk_rating: int = Field(..., ge=1, le=9, description="1-9 per the bank's rating scale")
    key_financials: str = Field(..., max_length=1200)
    risks: list[RiskFactor] = Field(..., min_length=2, max_length=10)
    covenants: list[CovenantRecommendation] = Field(..., min_length=1, max_length=6)
    policy_exceptions: list[str] = Field(
        default_factory=list,
        description="Any underwriting standards the deal does NOT meet; must be noted.",
    )
