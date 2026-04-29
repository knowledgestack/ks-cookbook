# Knowledge Stack with LangGraph

LangGraph is the right choice when retrieval and drafting are **separate, named steps** you want to inspect, retry, or branch on. This page ports the credit memo flagship to an explicit `retrieve → draft → review` graph.

## Install

```bash
uv add langgraph langchain-openai langchain-mcp-adapters
```

## Mental model

```
   ┌──────────┐    ┌────────┐    ┌────────┐
   │ retrieve │ ─► │ draft  │ ─► │ review │
   │  (KS)    │    │ (LLM)  │    │ (LLM)  │
   └──────────┘    └────────┘    └────────┘
        │              │              │
        ▼              ▼              ▼
     chunks[]      memo (raw)     memo (final)
```

Each node is a function over typed state. KS calls live in **one** node so you can independently set timeouts, retries, and tracing on retrieval vs generation.

## Worked example — credit memo (LangGraph port)

### State

```python
from typing import TypedDict
from pydantic import BaseModel

class Chunk(BaseModel):
    chunk_id: str
    path_part_id: str
    document_name: str
    text: str

class State(TypedDict):
    borrower: str
    loan_amount: int
    chunks: list[Chunk]
    memo: "CreditMemo | None"
```

### Retrieve node — explicit search → read loop

```python
import os
from langchain_mcp_adapters.client import MultiServerMCPClient

_client = MultiServerMCPClient({
    "knowledgestack": {
        "command": "uvx",
        "args": ["knowledgestack-mcp"],
        "transport": "stdio",
        "env": {"KS_API_KEY": os.environ["KS_API_KEY"]},
    },
})

QUERIES = [
    "credit policy risk rating scale",
    "underwriting standards leverage DSCR",
    "{borrower} financial statements",
    "{borrower} business plan industry",
]

async def retrieve_node(state: State) -> dict:
    tools = {t.name: t for t in await _client.get_tools()}
    chunks: list[Chunk] = []
    for q in QUERIES:
        hits = await tools["search_knowledge"].ainvoke({"query": q.format(**state)})
        for h in hits[:3]:
            body = await tools["read"].ainvoke({"path_part_id": h["path_part_id"]})
            for marker in extract_chunks(body):  # parse [chunk:<uuid>] blocks
                chunks.append(Chunk(**marker, path_part_id=h["path_part_id"]))
    return {"chunks": chunks}
```

### Draft + review nodes

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0)

async def draft_node(state: State) -> dict:
    context = "\n\n".join(f"[chunk:{c.chunk_id}] {c.text}" for c in state["chunks"])
    structured = llm.with_structured_output(CreditMemo)
    memo = await structured.ainvoke([
        ("system", DRAFT_SYSTEM),
        ("user", f"Borrower: {state['borrower']}\nLoan: ${state['loan_amount']:,}\n\n{context}"),
    ])
    return {"memo": memo}

async def review_node(state: State) -> dict:
    # Reject memos whose citations don't appear in retrieved chunks.
    valid = {c.chunk_id for c in state["chunks"]}
    bad = [cit for r in state["memo"].risks for cit in r.citations if cit.chunk_id not in valid]
    if bad:
        raise ValueError(f"{len(bad)} fabricated citations — re-running")
    return {}
```

### Compile the graph

```python
from langgraph.graph import StateGraph, END

g = StateGraph(State)
g.add_node("retrieve", retrieve_node)
g.add_node("draft",    draft_node)
g.add_node("review",   review_node)
g.set_entry_point("retrieve")
g.add_edge("retrieve", "draft")
g.add_edge("draft", "review")
g.add_edge("review", END)
graph = g.compile()

memo = (await graph.ainvoke({"borrower": "ACME Corp", "loan_amount": 5_000_000}))["memo"]
```

## Why this shape pays off

- **Retrieval is deterministic.** `retrieve_node` is just a list of named queries; you can snapshot, replay, or unit-test it without an LLM.
- **`review_node` is the citation enforcer.** Rejecting fabricated `chunk_id`s as a graph edge gives you measurable hallucination control, not just hope.
- **Concurrency.** For batch workloads (e.g. CSV enrichment over 5k rows), wrap `retrieve_node` + `draft_node` as a subgraph and fan out with `Send`.

## Real flagship using this pattern

[`flagships/csv_enrichment`](../../../flagships/csv_enrichment/) uses a small LangGraph state machine to enrich CSV rows in parallel. [`flagships/audit_workpaper_drafter`](../../../flagships/audit_workpaper_drafter/) uses retrieve → cite → draft → review.

## Gotchas

- **One MCP client per process**, not per node invocation. Reconstructing `MultiServerMCPClient` per call leaks subprocess handles fast.
- **`extract_chunks` is your contract with KS.** Parse the `[chunk:<uuid>]` markers carefully; that's how grounding works downstream.
- For chat-style streaming use `graph.astream(...)`; for batch / Temporal use `graph.ainvoke(...)`.
