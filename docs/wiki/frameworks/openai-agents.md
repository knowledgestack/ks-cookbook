# Knowledge Stack with OpenAI Agents SDK

The [openai-agents-python](https://github.com/openai/openai-agents-python) SDK has **native MCP support** — `MCPServerStdio` is a first-class type. This is the smallest framework wrapper around KS short of speaking MCP directly.

## Install

```bash
uv add openai-agents
```

## Env

```env
KS_API_KEY=sk-user-...
OPENAI_API_KEY=sk-proj-...
```

## Worked example — credit memo (Agents SDK port)

```python
import os, asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from pydantic import BaseModel, Field

# Same schema as the pydantic-ai flagship.
class Citation(BaseModel):
    chunk_id: str
    document_name: str
    snippet: str = Field(..., max_length=240)

class RiskFactor(BaseModel):
    label: str
    severity: str
    rationale: str
    citations: list[Citation]

class CreditMemo(BaseModel):
    borrower: str
    risk_rating: int = Field(..., ge=1, le=9)
    risks: list[RiskFactor]
    covenants: list[str]
    policy_exceptions: list[str]

SYSTEM = """You are a commercial credit analyst at Riverway Bank.
Workflow: search_knowledge(...) → read(path_part_id=...) → emit one CreditMemo JSON.
Every Citation.chunk_id must be copied verbatim from a [chunk:<uuid>] marker.
"""

async def draft_memo(borrower: str, loan_amount: int) -> CreditMemo:
    mcp = MCPServerStdio(
        params={
            "command": "uvx",
            "args": ["knowledgestack-mcp"],
            "env": {
                "KS_API_KEY": os.environ["KS_API_KEY"],
                "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
            },
        },
    )
    async with mcp:
        agent = Agent(
            name="KS credit analyst",
            model="gpt-4o",
            instructions=SYSTEM,
            mcp_servers=[mcp],
            output_type=CreditMemo,
        )
        result = await Runner.run(
            agent,
            f"Loan request: ${loan_amount:,} for {borrower}. Draft the credit memo.",
            max_turns=40,
        )
    return result.final_output

if __name__ == "__main__":
    print(asyncio.run(draft_memo("ACME Corp", 5_000_000)).model_dump_json(indent=2))
```

## Built-in features worth using

- **`output_type=CreditMemo`** — pydantic schema enforced by the SDK, same as pydantic-ai.
- **Agents traces.** Tool calls show up in the OpenAI dashboard with KS tool names (`search_knowledge`, `read`, …) for free.
- **Handoffs.** Pass control between agents with `agent.handoff(other)` — useful when you want a "researcher" to hand a corpus bundle to a "drafter" without leaving the SDK.
- **Guardrails.** `input_guardrail` / `output_guardrail` decorators are a clean place to enforce "every chunk_id must come from a previous read() call."

## Citation guardrail (recommended)

```python
from agents import output_guardrail, GuardrailFunctionOutput

@output_guardrail
async def citations_grounded(ctx, agent, output: CreditMemo) -> GuardrailFunctionOutput:
    seen_chunk_ids = ctx.context.get("seen_chunk_ids", set())  # populated by tool-result hook
    bad = [c.chunk_id for r in output.risks for c in r.citations if c.chunk_id not in seen_chunk_ids]
    return GuardrailFunctionOutput(
        output_info={"fabricated_citations": bad},
        tripwire_triggered=bool(bad),
    )

agent = Agent(..., output_guardrails=[citations_grounded])
```

The `seen_chunk_ids` set is built up from `read()` tool results via a tool callback. Once you have this, fabrication becomes a hard error rather than a "hopefully the LLM didn't lie."

## Multi-agent handoff

```python
researcher = Agent(name="researcher", mcp_servers=[mcp], instructions="Gather + cite passages.")
drafter    = Agent(name="drafter",    mcp_servers=[mcp], instructions="Draft the memo from passages.",
                   output_type=CreditMemo,
                   handoff_description="Hand off when you have enough cited material.")
researcher.handoffs = [drafter]
result = await Runner.run(researcher, prompt)
```

Equivalent to the [CrewAI multi-agent crew](crewai.md) but inside one runtime.

## Gotchas

- **`async with mcp:`** is required. Without it the server isn't started; tool calls fail silently as "tool not found."
- **`max_turns=40`** is a sane cap. KS retrieval normally settles in ~10–20 turns; >40 means the agent is stuck in a search loop, usually because it's passing `chunk_id` to `read()`.
- **Tracing keys.** The KS API key goes in the MCP `env`, not in `Runner.run` context. Don't leak it into the OpenAI trace.
