"""Structured output for ChiroCRM visit autopilot."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class CodeLine(BaseModel):
    code: str
    code_type: str = Field(..., pattern="^(CPT|ICD-10|HCPCS|MOD)$")
    description: str = Field(..., max_length=240)
    units: int = Field(..., ge=1, le=20)
    fee_cad: float = Field(..., ge=0)
    fee_citation: Citation
    justification_citation: Citation


class PriorAuthCriterion(BaseModel):
    criterion: str = Field(..., max_length=300)
    met: bool
    chart_citation: Citation | None = None
    policy_citation: Citation


class PatientPlanStep(BaseModel):
    visit_window: str = Field(..., description="e.g. 'weeks 1-2'")
    focus: str = Field(..., max_length=240)
    plain_language_instruction: str = Field(..., max_length=400)
    protocol_citation: Citation


class VisitAutopilotOutput(BaseModel):
    patient_id: str
    visit_date: str
    chief_complaint: str = Field(..., max_length=240)
    codes: list[CodeLine] = Field(..., min_length=1, max_length=12)
    prior_auth_required: bool
    prior_auth_criteria: list[PriorAuthCriterion] = Field(default_factory=list, max_length=10)
    prior_auth_letter_body: str | None = Field(default=None, max_length=2500)
    patient_plan: list[PatientPlanStep] = Field(..., min_length=1, max_length=8)
    clinician_note: str = Field(..., max_length=800)
