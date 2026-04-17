"""Folder-tree navigation: list children, fuzzy-find by name, introspect a node."""


from typing import Annotated, Any
from uuid import UUID

import ksapi
from ksapi.api.folders_api import FoldersApi
from ksapi.api.path_parts_api import PathPartsApi
from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ks_mcp.client import get_api_client
from ks_mcp.errors import is_not_found, rest_to_mcp
from ks_mcp.schema import PathPartAncestry, PathPartInfo


def _pp_info(pp: Any) -> PathPartInfo | None:
    inner = getattr(pp, "actual_instance", None) or pp
    path_part_id = (
        getattr(inner, "path_part_id", None) or getattr(inner, "id", None)
    )
    if path_part_id is None:
        return None
    return PathPartInfo(
        path_part_id=path_part_id,
        name=getattr(inner, "name", ""),
        part_type=str(getattr(inner, "part_type", "UNKNOWN")),
        materialized_path=getattr(inner, "materialized_path", None),
    )


def _filter_pp_infos(items: list[Any]) -> list[PathPartInfo]:
    out: list[PathPartInfo] = []
    for i in items:
        info = _pp_info(i)
        if info is not None:
            out.append(info)
    return out


def _resolve_folder_id(client: Any, folder_id: UUID) -> UUID:
    """Accept either a folder id or a folder path_part id.

    Agent loops often reuse the ``path_part_id`` returned by ``list_contents``.
    The KS folders API expects the underlying folder metadata id for nested
    listings, so resolve path-part ids to the backing folder id when possible.
    """
    path_parts = PathPartsApi(client)
    try:
        pp = path_parts.get_path_part(path_part_id=folder_id)
    except ksapi.ApiException as exc:
        if is_not_found(exc):
            return folder_id
        raise rest_to_mcp(exc) from exc

    if str(getattr(pp, "part_type", "")) != "FOLDER":
        return folder_id

    metadata_obj_id = getattr(pp, "metadata_obj_id", None)
    return metadata_obj_id or folder_id


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def list_contents(
        folder_id: Annotated[
            UUID | None,
            Field(description="Folder PDO id. Omit to list root-level folders in the tenant."),
        ] = None,
    ) -> list[PathPartInfo]:
        """List the immediate children of a folder.

        Pass no argument to list root-level folders. Returns one entry per
        child (folder or document) with its path-part id, name, and type.
        """
        client = get_api_client()
        folders = FoldersApi(client)
        try:
            if folder_id is None:
                root = folders.list_folders()
            else:
                resolved_folder_id = _resolve_folder_id(client, folder_id)
                root = folders.list_folder_contents(folder_id=resolved_folder_id)
        except ksapi.ApiException as exc:
            if folder_id is not None and is_not_found(exc):
                # Agents frequently recycle stale or hallucinated folder ids.
                # Falling back to tenant root keeps discovery moving without
                # requiring the caller to already know the folder structure.
                root = folders.list_folders()
            else:
                raise rest_to_mcp(exc) from exc
        items = getattr(root, "items", None) or root or []
        return _filter_pp_infos(items)

    @mcp.tool()
    def find(
        query: Annotated[str, Field(description="Fuzzy substring of the path-part's name.", min_length=1, max_length=255)],
        parent_path_part_id: Annotated[
            UUID | None,
            Field(description="Restrict search to descendants of this folder. Omit for whole tenant."),
        ] = None,
    ) -> list[PathPartInfo]:
        """Fuzzy-search path-parts (folders, documents, sections) by name.

        Use when the user refers to a document by a remembered title fragment.
        """
        client = get_api_client()
        folders = FoldersApi(client)
        try:
            result = folders.search_items(
                name_like=query, parent_path_part_id=parent_path_part_id
            )
        except ksapi.ApiException as exc:
            raise rest_to_mcp(exc) from exc
        items = getattr(result, "items", None) or result or []
        return _filter_pp_infos(items)

    @mcp.tool()
    def get_info(
        path_part_id: Annotated[UUID, Field(description="Any PDO id — folder, document, section, or chunk.")],
    ) -> PathPartAncestry:
        """Return a path-part's own info plus its root-to-leaf ancestry breadcrumb.

        Use when you need to resolve a node's type or build a human-readable
        path before calling ``read``.
        """
        client = get_api_client()
        api = PathPartsApi(client)
        try:
            node = api.get_path_part(path_part_id=path_part_id)
            ancestry_resp = api.get_path_part_ancestry(path_part_id=path_part_id)
        except ksapi.ApiException as exc:
            if is_not_found(exc):
                raise ValueError("path_part not found") from exc
            raise rest_to_mcp(exc) from exc

        ancestry_items = (
            getattr(ancestry_resp, "ancestors", None)
            or getattr(ancestry_resp, "items", None)
            or []
        )
        node_info = _pp_info(node)
        if node_info is None:
            raise ValueError("path_part lookup returned no id")
        return PathPartAncestry(
            node=node_info,
            ancestry=_filter_pp_infos(ancestry_items),
        )
