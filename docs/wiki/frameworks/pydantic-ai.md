# Knowledge Stack with pydantic-ai

> **Used by every flagship in this repo.** This is the reference implementation — start here if you want to see the canonical pattern.

pydantic-ai pairs a structured `output_type` with native MCP support, which is why every flagship is built on it. Every other framework page in this wiki ports the same flow.

## Install

```bash
uv add pydantic-ai
# MCP server (consumed via uvx — no local install needed):
uvx knowledgestack-mcp --help
```

## Env

```env
KS_API_KEY=sk-user-...
KS_BASE_URL=https://api.knowledgestack.ai
OPENAI_API_KEY=sk-proj-...
```

## Anatomy of a flagship

Every flagship in `flagships/*/` follows this four-file shape:

```
flagships/<name>/src/<module>/
  __main__.py     # CLI: argparse, env, calls agent.draft_*()
  agent.py        # prompt + MCPServerStdio + Agent(output_type=Schema)
  schema.py       # pydantic models — including Citation(chunk_id, document_name, snippet)
  sample_inputs/  # default demo input
```

## Worked example — credit memo drafter

Port-faithful to `flagships/credit_memo_drafter/src/credit_memo_drafter/agent.py`.

### Schema (citations are first-class)

```python
# schema.py
from pydantic import BaseModel, Field

class Citation(BaseModel):
    chunk_id: str = Field(..., description="UUID copied verbatim from a [chunk:<uuid>] marker.")
    document_name: str
    snippet: str = Field(..., max_length=240)

class RiskFactor(BaseModel):
    label: str
    severity: str  # "low" | "medium" | "high"
    rationale: str
    citations: list[Citation]

class CreditMemo(BaseModel):
    borrower: str
    risk_rating: int = Field(..., ge=1, le=9)
    risks: list[RiskFactor]
    covenants: list[str]
    policy_exceptions: list[str]
```

### Agent

```python
# agent.py
import os
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.usage import UsageLimits

SYSTEM = """You are a commercial credit analyst at Riverway Bank.

MANDATORY workflow:
1. search_knowledge(query=...) — natural-language questions, no folder_id.
2. read(path_part_id=<hit.path_part_id>) — never pass chunk_id; it 404s.
3. Every Citation.chunk_id MUST be copied verbatim from a [chunk:<uuid>] marker
   in read() output. Never fabricate UUIDs.
4. Produce a CreditMemo. Do not wrap it under an extra key.
"""

async def draft_memo(borrower: str, loan_amount: int, model: str = "gpt-4o") -> CreditMemo:
    mcp = MCPServerStdio(
        command="uvx",
        args=["knowledgestack-mcp"],
        env={
            "KS_API_KEY": os.environ["KS_API_KEY"],
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    agent = Agent(
        model=f"openai:{model}",
        mcp_servers=[mcp],
        system_prompt=SYSTEM,
        output_type=CreditMemo,
        retries=4,
        output_retries=4,
    )
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Loan request: ${loan_amount:,} for {borrower}. Draft the credit memo.",
            usage_limits=UsageLimits(request_limit=200),
        )
    return result.output
```

### CLI

```python
# __main__.py
import argparse, asyncio, os
from credit_memo_drafter.agent import draft_memo

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--borrower", required=True)
    p.add_argument("--loan-amount", type=int, required=True)
    p.add_argument("--model", default=os.environ.get("MODEL", "gpt-4o"))
    args = p.parse_args()
    memo = asyncio.run(draft_memo(args.borrower, args.loan_amount, args.model))
    print(memo.model_dump_json(indent=2))
```

## Why pydantic-ai for this

- **`output_type=CreditMemo`** enforces the schema — invalid output triggers retries automatically (`output_retries=4`).
- **`mcp_servers=[mcp]`** + `async with agent.run_mcp_servers()` — lifecycle management is built in.
- **`UsageLimits(request_limit=200)`** caps tool-call loops so a runaway agent can't burn your tenant.

## Ports of this flagship

If you want to port credit_memo_drafter to another framework, every page in this wiki uses the **same prompt, same schema, same MCP wiring** — only the framework glue changes:

- [LangChain](langchain.md) · [LangGraph](langgraph.md) · [CrewAI](crewai.md) · [OpenAI Agents SDK](openai-agents.md) · [Temporal](temporal.md) · [Custom MCP](custom-mcp.md)

## Gotchas

- **Use `gpt-4o` or `claude-opus-4-x`.** `gpt-4o-mini` skips grounding and emits empty `citations`.
- **`output_retries` matters.** Models occasionally wrap the JSON under `{"CreditMemo": {...}}`; the retry loop catches that.
- **Don't call `agent.run` outside `run_mcp_servers()`.** The MCP server isn't started yet and tool calls 404.
