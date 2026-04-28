"""Structured output — clinical trial eligibility assessment."""

from enum import Enum

from pydantic import BaseModel, Field


class MatchStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"
    UNCERTAIN = "UNCERTAIN"


class Citation(BaseModel):
    chunk_id: str
    source_document: str = Field(
        ..., description="e.g. 'PROGRESS Trial Protocol' or 'CMS NCD 310.1'"
    )
    quote: str = Field(
        ...,
        max_length=400,
        description="Verbatim excerpt from the corpus text, <=400 chars.",
    )


class CriterionMatch(BaseModel):
    criterion_text: str = Field(
        ...,
        max_length=500,
        description="The inclusion or exclusion criterion being evaluated.",
    )
    criterion_type: str = Field(..., description="'inclusion' or 'exclusion'")
    match_status: MatchStatus
    rationale: str = Field(
        ...,
        max_length=800,
        description=(
            "Clinical reasoning: why this patient does or does not meet the criterion."
        ),
    )
    citations: list[Citation] = Field(..., min_length=1, max_length=5)


class EligibilityAssessment(BaseModel):
    trial_id: str = Field(..., description="ClinicalTrials.gov NCT identifier.")
    trial_title: str = Field(..., max_length=300, description="Official trial title.")
    patient_summary: str = Field(
        ...,
        max_length=600,
        description="Brief summary of the patient profile being evaluated.",
    )
    overall_eligibility: MatchStatus = Field(
        ...,
        description=(
            "Overall eligibility: ELIGIBLE if all inclusion met and no "
            "exclusion triggered, INELIGIBLE if any exclusion triggered "
            "or inclusion unmet, UNCERTAIN if information is missing."
        ),
    )
    criteria: list[CriterionMatch] = Field(
        ...,
        min_length=3,
        max_length=25,
        description="Each criterion evaluated against the patient profile.",
    )
    recommended_next_steps: str = Field(
        ...,
        max_length=500,
        description=(
            "Actionable next steps: additional tests needed, referral "
            "guidance, or confirmation of enrollment readiness."
        ),
    )
