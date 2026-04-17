"""Semantic + keyword search over the tenant's knowledge base."""


from typing import Annotated, Any
from uuid import UUID

import ksapi
from ksapi.api.chunks_api import ChunksApi
from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ks_mcp.client import get_api_client
from ks_mcp.errors import rest_to_mcp
from ks_mcp.schema import ChunkHit, ChunkType, SearchResult


def _build_search_request(
    query: str,
    top_k: int,
    parent_path_part_ids: list[UUID] | None,
    tag_ids: list[UUID] | None,
    distinct_files: bool,
    search_type: str,
) -> Any:
    return ksapi.ChunkSearchRequest(
        query=query,
        top_k=top_k,
        search_type=search_type,
        parent_path_part_ids=[str(p) for p in parent_path_part_ids]
            if parent_path_part_ids else None,
        tag_ids=[str(t) for t in tag_ids] if tag_ids else None,
        distinct_files=distinct_files,
    )


def _hit_from_scored_chunk(scored: Any) -> ChunkHit:
    chunk = getattr(scored, "chunk", scored)
    return ChunkHit(
        chunk_id=chunk.id,
        document_name=getattr(chunk, "document_name", None)
            or (chunk.document.name if getattr(chunk, "document", None) else "")
            or "",
        text=(getattr(chunk, "text", "") or ""),
        score=getattr(scored, "score", None),
        chunk_type=ChunkType(getattr(chunk, "chunk_type", ChunkType.TEXT.value)),
        path_part_id=getattr(chunk, "path_part_id", None),
    )


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def search_knowledge(
        query: Annotated[str, Field(description="Natural-language query for semantic retrieval.", min_length=1, max_length=4000)],
        top_k: Annotated[int, Field(description="Max number of chunks to return (1-50).", ge=1, le=50)] = 5,
        parent_path_part_ids: Annotated[
            list[UUID] | None,
            Field(description="Restrict search to descendants of these path-parts. Omit for whole tenant."),
        ] = None,
        tag_ids: Annotated[
            list[UUID] | None,
            Field(description="Only include chunks whose document carries all these tag UUIDs."),
        ] = None,
        distinct_files: Annotated[
            bool,
            Field(description="If true, at most one chunk per source document is returned."),
        ] = False,
    ) -> SearchResult:
        """Semantic (dense-vector) search over the tenant's chunks.

        Use for conceptual questions: returns passages semantically related
        to the query with a relevance score. For exact-term lookups prefer
        ``search_keyword`` instead.
        """
        api = ChunksApi(get_api_client())
        try:
            response = api.search_chunks(
                chunk_search_request=_build_search_request(
                    query, top_k, parent_path_part_ids, tag_ids, distinct_files, "dense_only"
                )
            )
        except ksapi.ApiException as exc:
            raise rest_to_mcp(exc) from exc
        items = getattr(response, "items", None) or response or []
        return SearchResult(hits=[_hit_from_scored_chunk(r) for r in items])

    @mcp.tool()
    def search_keyword(
        query: Annotated[str, Field(description="Keyword or phrase to match (BM25 full-text).", min_length=1, max_length=4000)],
        top_k: Annotated[int, Field(description="Max number of chunks to return (1-50).", ge=1, le=50)] = 5,
        parent_path_part_ids: Annotated[list[UUID] | None, Field(description="Restrict to descendants of these path-parts.")] = None,
        tag_ids: Annotated[list[UUID] | None, Field(description="Only chunks whose document carries all these tags.")] = None,
        distinct_files: Annotated[bool, Field(description="One chunk per source document when true.")] = False,
    ) -> SearchResult:
        """BM25 / keyword search over the tenant's chunks.

        Use when the user mentions a specific term, name, or quoted phrase.
        """
        api = ChunksApi(get_api_client())
        try:
            response = api.search_chunks(
                chunk_search_request=_build_search_request(
                    query, top_k, parent_path_part_ids, tag_ids, distinct_files, "full_text"
                )
            )
        except ksapi.ApiException as exc:
            raise rest_to_mcp(exc) from exc
        items = getattr(response, "items", None) or response or []
        return SearchResult(hits=[_hit_from_scored_chunk(r) for r in items])
