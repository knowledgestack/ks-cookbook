"""Pydantic input + output models for every MCP tool.

``FastMCP`` auto-generates JSON schemas from these, which is what the calling
agent framework (pydantic-ai, LangGraph, Claude Desktop, etc.) surfaces as
per-argument documentation. Good descriptions here == good tool use.
"""


from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ChunkType(str, Enum):
    TEXT = "TEXT"
    TABLE = "TABLE"
    IMAGE = "IMAGE"
    HTML = "HTML"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# Shared result shapes
# ---------------------------------------------------------------------------


class ChunkHit(BaseModel):
    chunk_id: UUID
    document_name: str = Field(..., description="Name of the owning document.")
    text: str = Field(..., description="Raw text of the chunk.")
    score: float | None = Field(
        None, description="Relevance score from the search backend (higher = better)."
    )
    chunk_type: ChunkType = Field(default=ChunkType.TEXT)
    path_part_id: UUID | None = None


class PathPartInfo(BaseModel):
    path_part_id: UUID
    name: str
    part_type: str = Field(
        ..., description="One of FOLDER | DOCUMENT | SECTION | CHUNK | THREAD_MESSAGE."
    )
    materialized_path: str | None = None


# ---------------------------------------------------------------------------
# Tool inputs
# ---------------------------------------------------------------------------


class SearchInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=4_000,
        description="Natural-language query for semantic search, or keyword phrase for BM25.")
    top_k: int = Field(default=5, ge=1, le=50,
        description="Maximum number of chunks to return.")
    parent_path_part_ids: list[UUID] | None = Field(
        default=None,
        description="Restrict search to descendants of these path-parts. None = whole tenant.",
    )
    tag_ids: list[UUID] | None = Field(
        default=None,
        description="Only include chunks whose owning document carries all these tags.",
    )
    distinct_files: bool = Field(
        default=False,
        description="If True, return at most one chunk per source document.",
    )


class ReadInput(BaseModel):
    path_part_id: UUID = Field(
        ...,
        description=(
            "Any PDO identifier — folder, document, section, or chunk. The tool "
            "dispatches to the appropriate read path."
        ),
    )
    max_chars: int = Field(
        default=4_000, ge=100, le=50_000,
        description="Truncate returned text to this many characters.",
    )


class ReadAroundInput(BaseModel):
    chunk_id: UUID = Field(..., description="Anchor chunk.")
    radius: int = Field(
        default=2, ge=0, le=10,
        description="Number of chunks before AND after the anchor to include.",
    )


class ListContentsInput(BaseModel):
    folder_id: UUID | None = Field(
        default=None,
        description="Folder PDO id. Omit to list root-level folders in the tenant.",
    )


class FindInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=256,
        description="Fuzzy-match substring of the path-part's name.")
    parent_path_part_ids: list[UUID] | None = Field(
        default=None,
        description="Restrict to descendants of these path-parts.",
    )


class GetInfoInput(BaseModel):
    path_part_id: UUID = Field(..., description="PDO id to describe.")


class ViewChunkImageInput(BaseModel):
    chunk_id: UUID = Field(..., description="IMAGE-type chunk to materialize.")


# ---------------------------------------------------------------------------
# Tool outputs (for the ones that return structured data; text/image come back
# as MCP content types)
# ---------------------------------------------------------------------------


class SearchResult(BaseModel):
    hits: list[ChunkHit]


class PathPartAncestry(BaseModel):
    node: PathPartInfo
    ancestry: list[PathPartInfo] = Field(
        ..., description="Root → … → parent, excluding the node itself."
    )


class OrganizationInfo(BaseModel):
    tenant_id: UUID
    name: str
    default_language: str = Field(
        ..., description="ISO-639 code, e.g. 'en'."
    )
    timezone: str = Field(..., description="IANA tz, e.g. 'America/New_York'.")


class CurrentDateTime(BaseModel):
    iso_utc: str = Field(..., description="Current time in UTC, ISO-8601.")
    iso_local: str = Field(
        ..., description="Current time in the tenant's timezone, ISO-8601."
    )
    timezone: str = Field(..., description="IANA tz used for ``iso_local``.")
