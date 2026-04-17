# CSV enrichment demo

Takes a CSV, enriches each row with a short summary pulled from your Knowledge Stack tenant, writes a new CSV. Built on **LangGraph** + `langchain-mcp-adapters`.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Any folder whose documents you want to enrich CSV rows against.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-csv`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
export KS_API_KEY="sk-user-..."
export ANTHROPIC_API_KEY="sk-ant-..."
uv run ks-cookbook-csv-enrich \
  --in sample_inputs/customers.csv \
  --out enriched.csv \
  --query-column query \
  --column research_summary \
  --concurrency 5
```

## Architecture

```
 load CSV ──▶ LangGraph enrich node ──▶ write CSV
                │
                ▼
   for each row (concurrency=N):
       create_react_agent([search_knowledge, read, ...]).ainvoke(row.query)
```

- **MCP tools come from `knowledgestack-mcp`** via `MultiServerMCPClient` — same tools the research-brief demo uses.
- **Concurrency-bounded** with `asyncio.Semaphore`. Default 5 — raise carefully; KS applies a per-key daily quota.
- **Partial-failure tolerant** — a single-row exception becomes `ERROR: <type>: <msg>` in the output cell and the rest of the CSV keeps going. Pass `--fail-fast` to opt out.

## Customise

Swap Anthropic for OpenAI: edit `graph.py` and replace `ChatAnthropic(...)` with
`ChatOpenAI(...)` — no other changes.
