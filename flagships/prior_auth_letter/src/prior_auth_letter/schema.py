"""Structured output the agent must return for each prior-auth letter."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str = Field(
        ...,
        description="UUID copied verbatim from a [chunk:<uuid>] marker.",
    )
    document_name: str = Field(..., description="Plan document the citation is from.")
    snippet: str = Field(..., max_length=500, description="Short supporting quote.")


class PriorAuthLetter(BaseModel):
    member_name: str = Field(..., min_length=1, max_length=200)
    member_dob: str = Field(..., description="Date of birth (free-form string).")
    member_id: str = Field(..., description="Health-plan member ID.")
    requested_service: str = Field(
        ...,
        min_length=1,
        max_length=400,
        description="CPT/HCPCS code or drug name + dose + quantity.",
    )
    ordering_provider: str = Field(..., min_length=1, max_length=200)
    clinical_scenario: str = Field(
        ...,
        min_length=1,
        max_length=3_000,
        description="3-6 sentences on presentation, duration, impairment.",
    )
    medical_necessity: str = Field(
        ...,
        min_length=1,
        max_length=4_000,
        description=(
            "Explicit medical-necessity argument mapping the patient's clinical facts "
            "to the plan's MPB criteria, with inline [n] references."
        ),
    )
    prior_therapies: str = Field(
        ...,
        min_length=1,
        max_length=2_000,
        description="Each prior treatment with name, dose, duration, outcome.",
    )
    supporting_evidence: str = Field(
        default="",
        max_length=1_500,
        description="Optional society-guideline or literature references.",
    )
    citations: list[Citation] = Field(
        ...,
        min_length=1,
        max_length=20,
        description=(
            "Citations supporting the letter. Every chunk_id MUST have appeared "
            "verbatim in a [chunk:<uuid>] marker from the read tool."
        ),
    )
