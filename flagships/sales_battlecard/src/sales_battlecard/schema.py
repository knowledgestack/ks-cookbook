"""Structured output for Sales Battlecard Generator."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class Battlecard(BaseModel):
    competitor: str
    key_differentiators: list[str] = Field(..., min_length=2)
    common_objections: list[str] = Field(..., min_length=2)
    win_themes: list[str] = Field(..., min_length=1)
    citations: list[Citation] = Field(..., min_length=1)
