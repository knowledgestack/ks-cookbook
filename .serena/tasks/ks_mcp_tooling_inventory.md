# KS MCP Tooling Inventory (v1)

Source of truth: `mcp-python/src/ks_mcp/server.py` and
`mcp-python/src/ks_mcp/tools/*`.

The cookbook exposes exactly 10 read-side KS MCP tools:

## Search

1. `search_knowledge`
- Semantic (dense-vector) chunk retrieval.
- Use for conceptual questions.

2. `search_keyword`
- BM25/full-text chunk retrieval.
- Use for exact names, phrases, or quoted terms.

## Read

3. `read`
- Read any KS path-part (`FOLDER`/`DOCUMENT`/`SECTION`/`CHUNK`) by
  `path_part_id`.
- For documents, returns assembled text with chunk tags where available.

4. `read_around`
- Fetch neighboring chunks around an anchor `chunk_id`.
- Use to expand context around a hit before writing an answer.

5. `view_chunk_image`
- Materialize image bytes for IMAGE-type chunks.
- Returns MCP `ImageContent`.

## Browse

6. `list_contents`
- List folder children.
- No argument lists root folders.

7. `find`
- Fuzzy name search over path-parts.
- Optional parent scoping.

8. `get_info`
- Resolve path-part metadata + ancestry breadcrumb.
- Use for type/path disambiguation before reading.

## Tenant Context

9. `get_organization_info`
- Tenant metadata: id, name, language, timezone.

10. `get_current_datetime`
- Current UTC and tenant-local datetime.

## Usage heuristic

1. Discover scope (`list_contents`/`find`/`get_info`).
2. Retrieve evidence (`search_knowledge` or `search_keyword`).
3. Expand evidence (`read` and `read_around`).
4. Cite KS chunks in final outputs.

Writes are intentionally excluded in v1.
