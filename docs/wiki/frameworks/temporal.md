# Knowledge Stack with Temporal

Use KS inside **Temporal activities** when you need durable, retriable, cross-service workflows — bulk document processing, scheduled re-runs, long-running orchestration with human approvals. Temporal owns the workflow; KS is called from activities.

## Install

```bash
uv add temporalio openai pydantic-ai mcp
```

## Architecture

```
   ┌─────────────── Workflow (deterministic) ───────────────┐
   │                                                        │
   │   activity:retrieve_chunks ──► activity:draft_memo ──► │
   │      (KS MCP calls)              (LLM call)            │
   │                                                        │
   └────────────────────────────────────────────────────────┘
                         │
                         ▼
                  durable history
                  (replay-safe)
```

**Key rule:** workflows must be deterministic. **Never** call KS, an LLM, or any I/O from workflow code — only from activities.

## Worked example — credit memo (Temporal port)

### Activity 1: retrieve from KS

```python
# activities.py
from dataclasses import dataclass
from temporalio import activity
from recipes._shared.mcp_client import ks_mcp_session  # or roll your own

@dataclass
class Chunk:
    chunk_id: str
    path_part_id: str
    document_name: str
    text: str

@dataclass
class RetrieveInput:
    borrower: str

@activity.defn
async def retrieve_chunks(inp: RetrieveInput) -> list[Chunk]:
    queries = [
        "credit policy risk rating scale",
        "underwriting standards leverage DSCR",
        f"{inp.borrower} financial statements",
        f"{inp.borrower} business plan",
    ]
    out: list[Chunk] = []
    async with ks_mcp_session() as session:
        for q in queries:
            hits = await session.call_tool("search_knowledge", {"query": q})
            for h in hits[:3]:
                body = await session.call_tool("read", {"path_part_id": h["path_part_id"]})
                out.extend(parse_chunks(body, h["path_part_id"]))
    return out
```

### Activity 2: draft via LLM

```python
@dataclass
class DraftInput:
    borrower: str
    loan_amount: int
    chunks: list[Chunk]

@activity.defn
async def draft_memo(inp: DraftInput) -> CreditMemo:
    # pydantic-ai or OpenAI SDK call here — no MCP, just the LLM
    return await llm_draft(inp.borrower, inp.loan_amount, inp.chunks)
```

### Workflow

```python
# workflow.py
from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import retrieve_chunks, draft_memo, RetrieveInput, DraftInput

@workflow.defn
class CreditMemoWorkflow:
    @workflow.run
    async def run(self, borrower: str, loan_amount: int) -> CreditMemo:
        chunks = await workflow.execute_activity(
            retrieve_chunks,
            RetrieveInput(borrower=borrower),
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=workflow.RetryPolicy(maximum_attempts=3),
        )
        memo = await workflow.execute_activity(
            draft_memo,
            DraftInput(borrower=borrower, loan_amount=loan_amount, chunks=chunks),
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=workflow.RetryPolicy(maximum_attempts=2),
        )
        return memo
```

### Worker

```python
# worker.py
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

async def main() -> None:
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="credit-memo",
        workflows=[CreditMemoWorkflow],
        activities=[retrieve_chunks, draft_memo],
    )
    await worker.run()

asyncio.run(main())
```

## Patterns that pay off

- **Split retrieval and generation into separate activities.** Different timeouts, different retry policies. KS calls are fast and idempotent; LLM calls are slow and expensive.
- **Pin the MCP server version in your worker image.** Workflow replays can span days; an MCP server upgrade mid-flight will surprise you.
- **Bulk processing fan-out.** For "draft 5,000 memos overnight", start a parent workflow that spawns child workflows via `workflow.start_child_workflow` — Temporal handles concurrency, retries, and progress tracking.
- **Human-in-the-loop.** Wrap the reviewer step as a signal: workflow waits on `await workflow.wait_condition(lambda: self._approved)`, a human approves via Temporal Web, workflow resumes.

## Idempotency

KS reads are idempotent — replaying `retrieve_chunks` is safe. The LLM call in `draft_memo` is **not** idempotent (different sampling). If you need byte-identical replays, cache the LLM response keyed by `(borrower, loan_amount, hash(chunks))` in `draft_memo` itself.

## Permissions across workflows

- One `KS_API_KEY` per worker → all workflows on that worker share that scope.
- Multi-tenant: pass tenant `KS_API_KEY` via activity input (encrypted) and override per-call MCP env. Don't leak keys into workflow inputs (they're in the durable history).

## Gotchas

- **No KS / LLM calls in workflow code.** They're non-deterministic. Workflow body coordinates; activities do work.
- **`workflow.unsafe.imports_passed_through()`** is required when importing activity modules that import non-deterministic libs (mcp client, openai sdk).
- **Activity timeouts must exceed the slowest KS read.** A `read_around` over a 200-page PDF can take a few seconds; budget accordingly.
- **Don't share MCP sessions across activities.** Open + close inside each activity body. The server is cheap to start (sub-second under `uvx`).
