# Knowledge Stack with LangChain

Port of the [pydantic-ai credit memo flagship](pydantic-ai.md#worked-example--credit-memo-drafter) to LangChain. Same prompt, same schema, same MCP server — only the framework glue changes.

## Install

```bash
uv add langchain langchain-openai langchain-mcp-adapters langgraph
```

## Env

```env
KS_API_KEY=sk-user-...
OPENAI_API_KEY=sk-proj-...
```

## Pattern: KS MCP tools as LangChain tools

`langchain-mcp-adapters` wraps every KS MCP tool (`search_knowledge`, `read`, `list_contents`, …) as a LangChain `BaseTool`. Hand them to a ReAct agent and you're done.

```python
import os, asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

async def get_ks_tools():
    client = MultiServerMCPClient({
        "knowledgestack": {
            "command": "uvx",
            "args": ["knowledgestack-mcp"],
            "transport": "stdio",
            "env": {
                "KS_API_KEY": os.environ["KS_API_KEY"],
                "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
            },
        },
    })
    return await client.get_tools()
```

## Worked example — credit memo (LangChain port)

### Schema (pydantic, same as flagship)

```python
from pydantic import BaseModel, Field

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
```

### Agent

```python
SYSTEM = """You are a commercial credit analyst at Riverway Bank.

MANDATORY workflow:
1. search_knowledge(query=...) — natural-language questions, no folder_id.
2. read(path_part_id=<hit.path_part_id>) — never pass chunk_id.
3. Every Citation.chunk_id MUST be copied verbatim from a [chunk:<uuid>] marker.
4. Return ONE JSON object that matches the CreditMemo schema. No prose around it.
"""

async def draft_memo(borrower: str, loan_amount: int) -> CreditMemo:
    tools = await get_ks_tools()
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured = llm.with_structured_output(CreditMemo)

    agent = create_react_agent(llm, tools, prompt=SYSTEM)
    raw = await agent.ainvoke({
        "messages": [("user", f"Loan request: ${loan_amount:,} for {borrower}. Draft the memo.")]
    })

    # Final assistant message → structured output
    final_text = raw["messages"][-1].content
    return await structured.ainvoke([("system", SYSTEM), ("user", final_text)])

if __name__ == "__main__":
    print(asyncio.run(draft_memo("ACME Corp", 5_000_000)).model_dump_json(indent=2))
```

> The two-step pattern (ReAct loop → `with_structured_output`) is the cleanest way to keep tool-calling and JSON-shape enforcement separate. Combining both at once with `bind_tools` works but produces messier traces.

## Streaming the tool calls

```python
async for event in agent.astream_events(
    {"messages": [("user", prompt)]},
    version="v2",
):
    if event["event"] == "on_tool_start":
        print(f"→ {event['name']}({event['data']['input']})")
```

You'll see ~10–20 KS calls (`search_knowledge`, `read`, `read_around`) before the agent settles on the memo.

## Permissions

`KS_API_KEY` is what scopes retrieval. Use a **per-user key** if you're running this server-side on behalf of multiple users — don't share one shared key across tenants.

## Gotchas

- **Don't pass `chunk_id` to `read`.** It expects `path_part_id`. The agent will 404 in a loop until token budget runs out.
- **Set `temperature=0`.** ReAct + grounding is brittle at higher temperatures; the agent starts skipping `read()` calls.
- **`MultiServerMCPClient` keeps the server warm** across calls. Reuse one client per process; don't reconstruct it per request.
- **For LangGraph state machines** instead of a ReAct agent, see the [LangGraph page](langgraph.md).
