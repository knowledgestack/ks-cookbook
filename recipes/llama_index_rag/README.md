# LlamaIndex RAG (framework proof)

Proves the "any framework" claim: same auth pattern, same grounding, swap
the framework to [LlamaIndex](https://github.com/run-llama/llama_index).

```bash
uv pip install llama-index llama-index-embeddings-openai llama-index-llms-openai
uv run python recipes/llama_index_rag/recipe.py \
  --question "What are our access-control requirements?"
```

## Architecture

```
KS MCP (permission-filtered)  ──docs──▶  LlamaIndex VectorStoreIndex  ──answer──▶ stdout
      ↑
  KS_API_KEY (per-user)
```

The LlamaIndex side is vanilla — `VectorStoreIndex.from_documents(...)`,
`as_query_engine(...)`. The docs fed in have already been filtered by KS
according to the calling API key's `PathPermission` scope. LlamaIndex never
sees documents the user isn't allowed to read — KS filtered them before they
arrived.
