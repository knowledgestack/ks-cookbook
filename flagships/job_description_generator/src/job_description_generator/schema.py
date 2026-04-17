"""Structured output for Job Description Generator."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class JobDescription(BaseModel):
    title: str
    level: str
    department: str
    responsibilities: list[str] = Field(..., min_length=3)
    requirements: list[str] = Field(..., min_length=3)
    nice_to_haves: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(..., min_length=1)
