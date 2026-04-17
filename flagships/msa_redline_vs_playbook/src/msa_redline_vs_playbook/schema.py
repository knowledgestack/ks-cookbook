"""Structured output for the MSA redline-vs-playbook agent."""


from enum import Enum

from pydantic import BaseModel, Field


class DeviationSeverity(str, Enum):
    NONE = "NONE"
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    MISSING = "MISSING"


class ClauseComparison(BaseModel):
    clause_topic: str = Field(
        ...,
        max_length=120,
        description=(
            "Short topic name, e.g. 'Indemnification', 'Limitation of Liability', "
            "'Confidentiality', 'IP Ownership'."
        ),
    )
    playbook_position: str = Field(
        ...,
        max_length=800,
        description="Summary of the playbook's stance on this clause topic.",
    )
    inbound_position: str = Field(
        ...,
        max_length=800,
        description=(
            "Summary of the inbound contract's stance. "
            "If the topic is absent from the inbound, state 'NOT FOUND'."
        ),
    )
    deviation_severity: DeviationSeverity = Field(
        ...,
        description=(
            "NONE = positions match; MINOR = cosmetic or low-risk difference; "
            "MAJOR = materially different risk allocation; "
            "MISSING = clause absent from inbound contract."
        ),
    )
    recommended_change: str = Field(
        ...,
        max_length=600,
        description=(
            "Specific redline recommendation. For NONE: 'No change required'. "
            "For MISSING: suggest inserting the playbook clause."
        ),
    )
    playbook_citation: str = Field(
        ...,
        description="chunk_id from the playbook document [chunk:<uuid>] marker.",
    )
    inbound_citation: str = Field(
        default="",
        description=(
            "chunk_id from the inbound document [chunk:<uuid>] marker. "
            "Empty if the clause is MISSING from the inbound."
        ),
    )


class RedlineMemo(BaseModel):
    inbound_contract_name: str = Field(..., max_length=200)
    playbook_name: str = Field(..., max_length=200)
    executive_summary: str = Field(
        ...,
        max_length=600,
        description="2-3 sentence summary of overall deviation posture.",
    )
    clauses: list[ClauseComparison] = Field(
        ...,
        min_length=3,
        description=(
            "Clause-by-clause comparison. Must include at least: "
            "Indemnification, Limitation of Liability, Confidentiality, "
            "IP Ownership, and Term/Termination."
        ),
    )
