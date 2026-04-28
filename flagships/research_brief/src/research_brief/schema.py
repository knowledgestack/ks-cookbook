"""Structured output the agent produces; python-docx consumes this shape."""

from uuid import UUID

from pydantic import BaseModel, Field


class Citation(BaseModel):
    id: int = Field(..., description="1-indexed citation number used inline as [n].")
    chunk_id: UUID
    document_name: str
    snippet: str = Field(..., max_length=500, description="Short supporting quote.")
    page: int | None = Field(default=None, description="Page number if known.")


class Section(BaseModel):
    heading: str = Field(..., min_length=1, max_length=200)
    body: str = Field(
        ...,
        min_length=1,
        max_length=8_000,
        description="Paragraph prose with inline [n] references to citations.",
    )
    citation_ids: list[int] = Field(
        default_factory=list,
        description="Which citation numbers this section relies on.",
    )


class BriefOutput(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    sections: list[Section] = Field(..., min_length=1, max_length=12)
    citations: list[Citation] = Field(..., min_length=1, max_length=40)
