"""Structured output for the contract redline flagship."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class Redline(BaseModel):
    clause_title: str = Field(..., max_length=160)
    original_text: str = Field(..., max_length=1500)
    proposed_text: str = Field(..., max_length=1500)
    risk_tier: str = Field(..., pattern="^(blocker|major|minor|fallback)$")
    rationale: str = Field(..., max_length=800)
    offending_clause_citation: Citation
    playbook_rule_citation: Citation


class RedlineMemo(BaseModel):
    counterparty_document: str
    playbook_name: str
    summary: str = Field(..., max_length=1200)
    redlines: list[Redline] = Field(..., min_length=1, max_length=30)
    acceptable_as_is: list[str] = Field(default_factory=list)
