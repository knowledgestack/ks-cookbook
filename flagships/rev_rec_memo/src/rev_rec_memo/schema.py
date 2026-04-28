"""Structured output the agent produces for an ASC 606 rev-rec memo."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str = Field(
        ..., description="UUID copied verbatim from a [chunk:<uuid>] marker."
    )
    document_name: str = Field(..., max_length=200)
    snippet: str = Field(..., max_length=500, description="Short supporting quote.")


class Step(BaseModel):
    number: int = Field(..., ge=1, le=5)
    title: str = Field(..., min_length=1, max_length=200)
    analysis: str = Field(
        ...,
        min_length=40,
        max_length=4000,
        description=(
            "2-4 paragraph analysis for this ASC 606 step, "
            "referring to citations inline as [chunk:<uuid>]."
        ),
    )
    citation_chunk_ids: list[str] = Field(
        default_factory=list,
        description="Chunk ids this step's analysis relies on.",
    )


class RevRecMemo(BaseModel):
    customer: str = Field(..., max_length=200)
    product: str = Field(..., max_length=200)
    total_contract_value_usd: float = Field(..., ge=0)
    conclusion: str = Field(
        ...,
        min_length=40,
        max_length=2000,
        description="Short overall conclusion across the five steps.",
    )
    steps: list[Step] = Field(..., min_length=5, max_length=5)
    citations: list[Citation] = Field(
        default_factory=list,
        description=(
            "Every chunk_id referenced in any step's analysis must appear here "
            "exactly once, with its source document_name and a short snippet."
        ),
    )
