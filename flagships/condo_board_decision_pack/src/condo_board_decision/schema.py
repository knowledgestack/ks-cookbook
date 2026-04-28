"""Structured output for the condo board decision pack."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class GoverningRule(BaseModel):
    source: str = Field(..., description="Declaration | Bylaws | Rules | ACC Guidelines")
    rule_summary: str = Field(..., max_length=400)
    citation: Citation


class Precedent(BaseModel):
    meeting_date: str = Field(..., description="YYYY-MM-DD of past board meeting")
    similar_request: str = Field(..., max_length=300)
    outcome: str = Field(..., max_length=300)
    citation: Citation


class ReserveImpact(BaseModel):
    note: str = Field(..., max_length=400)
    citation: Citation | None = None


class BoardDecisionPack(BaseModel):
    request_summary: str = Field(..., max_length=500)
    unit: str
    verdict: str = Field(
        ..., pattern="^(APPROVE|APPROVE_WITH_CONDITIONS|DENY|REQUIRES_OWNER_VOTE)$"
    )
    required_vote_threshold: str = Field(
        ..., description="e.g. 'simple majority of board', '2/3 of owners', 'none required'"
    )
    governing_rules: list[GoverningRule] = Field(..., min_length=1, max_length=8)
    precedents: list[Precedent] = Field(default_factory=list, max_length=6)
    reserve_impact: ReserveImpact | None = None
    conditions: list[str] = Field(default_factory=list, max_length=8)
    rationale: str = Field(..., max_length=1500)
    recommended_motion: str = Field(..., max_length=500)
