# Research-brief demo


**Tags:** `research` `reports` `analyst`

Generates a **cited `.docx` research brief** from your Knowledge Stack tenant, using [pydantic-ai](https://ai.pydantic.dev) + the `knowledgestack-mcp` server.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Any folder with research-grade source material.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-research`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
export KS_API_KEY="sk-user-..."
export ANTHROPIC_API_KEY="sk-ant-..."   # or OPENAI_API_KEY
uv run ks-cookbook-research-brief --topic "CRISPR off-target effects" --out brief.docx
```

## What it does

1. Spawns `uvx knowledgestack-mcp` over stdio — the MCP server talks to KS with your API key.
2. Constructs a pydantic-ai `Agent` with:
   - System prompt: "research analyst; use tools; produce `BriefOutput`."
   - Structured result type: `BriefOutput` (title + sections + citations).
3. Agent iteratively calls `search_knowledge` + `read` / `read_around` until it has grounded content.
4. pydantic validates the final output → renders to `.docx` via `python-docx`.

## Why this shape

- **All tools go through MCP** — no framework lock-in; swap pydantic-ai for LangGraph or the OpenAI Agents SDK and only `agent.py` changes.
- **Output artifact, not chatbot** — the demo produces a file. Anyone can skim it and see it's real.
- **Citations are structured** — the agent emits `chunk_id` per reference, so the doc is trivially verifiable.
