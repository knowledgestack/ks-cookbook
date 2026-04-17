# MCP tool reference

`knowledgestack-mcp` v1 is **read-only**. It exposes ten tools across four functional groups. Your agent can rely on this surface — writes (ingest, delete, generate) are intentionally not available, so agents can't mutate tenant state.

All tools respect the caller's API-key permissions. A tool call that targets a folder the user can't see returns an error rather than silently empty results.

## Browse

### `list_contents`
Immediate children of a folder, as a list of path-parts with `path_part_id`, `name`, and `type`.
- **Use when** you know the folder and want to enumerate what's in it.
- **Args**: `folder_id: UUID`
- **Returns**: `list[PathPartInfo]`

### `find`
Fuzzy name search across folders, documents, and sections the caller can see.
- **Use when** the user refers to a document by name and you need its UUID.
- **Args**: `query: str`, optional `type` filter.
- **Returns**: ranked `list[PathPartInfo]`

### `get_info`
A path-part's own metadata plus its full root-to-leaf ancestry breadcrumb.
- **Use when** you need to show a citation's location in the tree, or resolve a document's parent folder.
- **Args**: `path_part_id: UUID`

## Read

### `read`
Read the contents of any path-part — folder, document, section, or chunk. Dispatches on part type. Chunks come back with `[chunk:<uuid>]` markers after each passage; **every citation your agent emits must be copied verbatim from one of these markers**.
- **Args**: `path_part_id: UUID`, optional pagination.

### `read_around`
Given a chunk UUID, return the `radius` chunks before and after it, concatenated.
- **Use when** a search hit is interesting but you need its surrounding context to quote it fairly.
- **Args**: `chunk_id: UUID`, `radius: int`

### `view_chunk_image`
Fetch the raw bytes of an `IMAGE`-type chunk and return it as MCP image content (for multimodal models).
- **Args**: `chunk_id: UUID`

## Search

### `search_knowledge`
Dense-vector semantic search over the tenant's chunks.
- **Use when** the user's question is conceptual and you want meaning-matched results, not exact phrasing.
- **Args**: `query: str`, optional `folder_id` scope, `limit`.
- **Returns**: ranked `list[ChunkHit]` with score, text, and `chunk_id`.

### `search_keyword`
BM25 keyword search over the same chunks.
- **Use when** you're looking for a specific phrase, identifier, or legal citation.
- **Same args** as `search_knowledge`.

Most flagships combine both: semantic search to find candidates, keyword search to anchor specific phrases, then `read` / `read_around` to pull full context before emitting citations.

## Tenant context

### `get_organization_info`
Caller's tenant id, name, default language, and timezone. Useful for localization and date formatting.

### `get_current_datetime`
Current datetime in UTC and in the tenant's local timezone. Use this instead of `datetime.now()` so agents give the user's "today," not the server's.

## Standard retrieval pattern

Most flagships follow this shape. It's worth memorizing:

```text
1. list_contents(folder_id=<corpus>)        # enumerate the corpus
2. search_knowledge(query=..., folder_id=…) # narrow to relevant chunks
3. read(path_part_id=<doc or section>)      # pull full passages + [chunk:<uuid>] markers
4. read_around(chunk_id=<hit>, radius=2)    # optional: widen context around a citation
5. emit structured output                    # citations = chunk UUIDs from step 3/4
```

## Rules for agent prompts

Every system prompt in this repo enforces the same invariants. If you're writing a new flagship, copy these:

- Enumerate with `list_contents` before reading.
- Pass **`path_part_id` UUIDs**, not document names, to `read`.
- Citations must be `[chunk:<uuid>]` values copied from `read` output. Do not synthesize UUIDs.
- When a fact isn't in the retrieved material, say so. Do not fabricate numbers.
