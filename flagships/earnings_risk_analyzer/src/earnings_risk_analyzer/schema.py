"""Structured output — an equity-research-style risk-flag memo."""


from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Category(str, Enum):
    MARKET = "Market"
    COMPETITION = "Competition"
    OPERATIONAL = "Operational"
    REGULATORY = "Regulatory"
    FINANCIAL = "Financial"
    TECHNOLOGY = "Technology"
    LEGAL = "Legal"
    CYBERSECURITY = "Cybersecurity"
    MACRO = "Macro/Economic"
    OTHER = "Other"


class Citation(BaseModel):
    chunk_id: str
    section: str = Field(..., description="e.g. 'Risk Factors (Item 1A)'")
    quote: str = Field(..., max_length=400,
        description="Verbatim excerpt from the 10-K text, <=400 chars.")


class RiskFlag(BaseModel):
    title: str = Field(..., max_length=120,
        description="Short headline (e.g. 'Revenue concentration in Workers product line').")
    category: Category
    severity: Severity
    analysis: str = Field(..., max_length=1500,
        description="Analyst-grade narrative: what the risk is, why it matters, how material.")
    mitigation: str = Field(..., max_length=500,
        description="What the company says they're doing (if anything) or what's missing.")
    citations: list[Citation] = Field(..., min_length=1, max_length=5)


class EarningsRiskMemo(BaseModel):
    company: str
    ticker: str
    filing_period: str = Field(..., description="e.g. 'FY2025 (Dec 31, 2025)'")
    overall_risk_posture: str = Field(..., max_length=200,
        description="One-sentence executive assessment.")
    flags: list[RiskFlag] = Field(..., min_length=5, max_length=15,
        description="Ordered by severity (CRITICAL first). 5-15 total.")
    new_risks_vs_prior_year: list[str] = Field(
        default_factory=list,
        description="Risks that appear NEW or materially changed vs the prior 10-K.",
    )
    investment_implications: str = Field(..., max_length=800,
        description="2-3 paragraph synthesis: what this means for the investment thesis.")
