"""Structured output for the Realtime SDR session summary."""


from pydantic import BaseModel, Field


class MeddicScore(BaseModel):
    metrics: str = Field(..., pattern="^(covered|partial|missing)$")
    economic_buyer: str = Field(..., pattern="^(covered|partial|missing)$")
    decision_criteria: str = Field(..., pattern="^(covered|partial|missing)$")
    decision_process: str = Field(..., pattern="^(covered|partial|missing)$")
    identify_pain: str = Field(..., pattern="^(covered|partial|missing)$")
    champion: str = Field(..., pattern="^(covered|partial|missing)$")


class SessionSummary(BaseModel):
    prospect: str
    mode: str = Field(..., pattern="^(text|voice)$")
    turns: int = Field(..., ge=1)
    tool_calls: int = Field(..., ge=0)
    meddic: MeddicScore
    discovered_pains: list[str] = Field(default_factory=list, max_length=10)
    open_objections: list[str] = Field(default_factory=list, max_length=10)
    next_step: str = Field(..., max_length=400)
