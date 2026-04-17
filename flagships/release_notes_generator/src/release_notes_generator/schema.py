"""Structured output for Release Notes Generator."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class ReleaseNotes(BaseModel):
    version: str
    date: str
    features: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    breaking_changes: list[str] = Field(default_factory=list)
    migration_steps: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(..., min_length=1)
