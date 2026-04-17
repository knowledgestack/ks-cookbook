# CSV enrichment demo

Takes a CSV, enriches each row with a short summary pulled from your Knowledge Stack tenant, writes a new CSV. Built on **LangGraph** + `langchain-mcp-adapters`.

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
