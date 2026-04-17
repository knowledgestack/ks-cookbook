"""Structured output for Employee Handbook Q&A."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class HandbookAnswer(BaseModel):
    question: str
    answer: str = Field(..., max_length=2000)
    policy_section: str = Field(..., max_length=200)
    citations: list[Citation] = Field(..., min_length=1)
