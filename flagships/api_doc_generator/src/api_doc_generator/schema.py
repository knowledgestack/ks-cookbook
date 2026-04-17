"""Structured output for API Documentation Generator."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=400)


class APIDoc(BaseModel):
    endpoint: str
    method: str
    description: str = Field(..., max_length=1000)
    parameters: list[str] = Field(default_factory=list)
    request_example: str = Field(..., max_length=1000)
    response_example: str = Field(..., max_length=1000)
    auth_requirements: str
    citations: list[Citation] = Field(..., min_length=1)
