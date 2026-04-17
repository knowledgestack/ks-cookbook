"""Read a PDO (document / section / chunk), read neighbours, view image chunks."""


import base64
from typing import Annotated, Any
from uuid import UUID

import httpx
import ksapi
from ksapi.api.chunks_api import ChunksApi
from ksapi.api.documents_api import DocumentsApi
from ksapi.api.path_parts_api import PathPartsApi
from ksapi.api.sections_api import SectionsApi
from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent
from pydantic import Field

from ks_mcp.client import get_api_client
from ks_mcp.errors import rest_to_mcp


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n...[truncated; {len(text) - limit} more chars]"


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def read(
        path_part_id: Annotated[UUID, Field(description="Any PDO id (folder, document, section, or chunk).")],
        max_chars: Annotated[int, Field(description="Truncate returned text to this many characters.", ge=100, le=50_000)] = 4000,
    ) -> str:
        """Read the contents of any PDO. Dispatches on part type.

        For documents/sections the structural outline is returned; for chunks
        the raw text. Use after ``find`` or ``search_*`` when you want full text.
        """
        client = get_api_client()
        path_parts = PathPartsApi(client)
        try:
            pp = path_parts.get_path_part(path_part_id=path_part_id)
        except ksapi.ApiException as exc:
            raise rest_to_mcp(exc) from exc

        part_type = getattr(pp, "part_type", "")
        metadata_obj_id = getattr(pp, "metadata_obj_id", None)

        try:
            if part_type == "CHUNK" and metadata_obj_id:
                chunk: Any = ChunksApi(client).get_chunk(chunk_id=metadata_obj_id)
                return _truncate(getattr(chunk, "text", "") or "", max_chars)

            if part_type == "SECTION" and metadata_obj_id:
                section: Any = SectionsApi(client).get_section(section_id=metadata_obj_id)
                body = getattr(section, "text", None) or getattr(section, "title", "")
                return _truncate(body or f"(section has no body: {pp.name})", max_chars)

            if part_type == "DOCUMENT" and metadata_obj_id:
                from ksapi.api.document_versions_api import DocumentVersionsApi
                doc: Any = DocumentsApi(client).get_document(document_id=metadata_obj_id)
                version_id = getattr(doc, "active_version_id", None)
                if version_id is None:
                    return getattr(doc, "name", pp.name)
                pieces: list[str] = [f"# {getattr(doc, 'name', pp.name)}\n"]
                offset = 0
                while True:
                    contents: Any = DocumentVersionsApi(client).get_document_version_contents(
                        version_id=version_id, limit=100, offset=offset,
                    )
                    items = getattr(contents, "items", None) or []
                    if not items:
                        break
                    for item in items:
                        inner = getattr(item, "actual_instance", None) or item
                        ptype = str(getattr(inner, "part_type", "")) or type(inner).__name__
                        name = getattr(inner, "name", "")
                        if "SECTION" in ptype or "Section" in type(inner).__name__:
                            pieces.append(f"\n## {name}\n")
                        else:
                            text = getattr(inner, "text", None) or getattr(inner, "content", "") or ""
                            chunk_id = getattr(inner, "id", None) or getattr(inner, "metadata_obj_id", None)
                            tag = f" [chunk:{chunk_id}]" if chunk_id else ""
                            if text:
                                pieces.append(f"{text}{tag}\n")
                    if len(items) < 100:
                        break
                    offset += 100
                return _truncate("".join(pieces), max_chars)

            return f"{pp.name} ({part_type}) — use list_contents to drill in."
        except ksapi.ApiException as exc:
            raise rest_to_mcp(exc) from exc

    @mcp.tool()
    def read_around(
        chunk_id: Annotated[UUID, Field(description="Anchor chunk id.")],
        radius: Annotated[int, Field(description="How many chunks before AND after the anchor to include.", ge=0, le=10)] = 2,
    ) -> str:
        """Return the ``radius`` chunks before and after an anchor chunk, concatenated.

        Great for pulling enough local context when a single chunk isn't enough.
        """
        api = ChunksApi(get_api_client())
        try:
            neighbours: Any = api.get_chunk_neighbors(chunk_id=chunk_id, radius=radius)
        except ksapi.ApiException as exc:
            raise rest_to_mcp(exc) from exc

        pieces: list[str] = []
        for item in getattr(neighbours, "items", []) or []:
            label = "ANCHOR" if getattr(item, "is_anchor", False) else "..."
            text = getattr(item, "text", "") or ""
            pieces.append(f"[{label}] {text}")
        return "\n\n".join(pieces) or "(no neighbours returned)"

    @mcp.tool()
    def view_chunk_image(
        chunk_id: Annotated[UUID, Field(description="IMAGE-type chunk id to materialize.")],
    ) -> ImageContent:
        """Fetch the image bytes for an IMAGE-type chunk and return them to the agent.

        Only works for chunks whose metadata carries at least one S3 URL.
        Agent frameworks that support multi-modal content will render inline.
        """
        api = ChunksApi(get_api_client())
        try:
            chunk: Any = api.get_chunk(chunk_id=chunk_id)
        except ksapi.ApiException as exc:
            raise rest_to_mcp(exc) from exc

        urls = getattr(chunk, "asset_s3_urls", None) or []
        if not urls:
            raise ValueError("Chunk has no image assets (not an IMAGE-type chunk).")

        with httpx.Client(timeout=30.0) as http:
            resp = http.get(urls[0])
            resp.raise_for_status()
            body = resp.content

        mime = resp.headers.get("content-type", "image/png")
        return ImageContent(
            type="image",
            data=base64.b64encode(body).decode(),
            mimeType=mime,
        )
