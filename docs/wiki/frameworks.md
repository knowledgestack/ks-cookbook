# Framework integrations

Knowledge Stack does not replace your agent runtime. It plugs in via **MCP** alongside whatever you already run. This is the index page — pick your framework for a worked example that ports a real flagship end-to-end.

## Pick your framework

| Framework | Best for | Page |
|---|---|---|
| **pydantic-ai** | Single-agent flagships with strict structured output. Reference impl. | [→ pydantic-ai](frameworks/pydantic-ai.md) |
| **LangChain** | ReAct-style agents, existing LangChain stacks, fast prototyping. | [→ LangChain](frameworks/langchain.md) |
| **LangGraph** | Explicit `retrieve → draft → review` graphs, branching, batch fan-out. | [→ LangGraph](frameworks/langgraph.md) |
| **CrewAI** | Multi-agent crews (researcher / drafter / reviewer) sharing one corpus. | [→ CrewAI](frameworks/crewai.md) |
| **OpenAI Agents SDK** | Native MCP, OpenAI dashboard tracing, handoffs + guardrails. | [→ OpenAI Agents SDK](frameworks/openai-agents.md) |
| **Temporal** | Durable, retriable enterprise workflows. Bulk + scheduled + human-in-loop. | [→ Temporal](frameworks/temporal.md) |
| **Claude Desktop / Cursor** | End-user assistants — KS in chat with no code. | [→ Claude Desktop & Cursor](frameworks/claude-desktop.md) |
| **Custom MCP client** | Non-Python runtimes, serverless, embedded services. | [→ Custom MCP](frameworks/custom-mcp.md) |

> **Every framework page ports the same flagship — `credit_memo_drafter` — so you can compare them side by side.** The prompt, schema, and MCP tools are identical; only the framework glue changes.

## The universal contract

Whatever framework you pick, KS expects the same five things. If your port doesn't honor these, citations and permissions break.

1. **Spawn `knowledgestack-mcp` with `KS_API_KEY` (and optional `KS_BASE_URL`) in env.** Never as a tool argument; the server reads it once at startup.
2. **One MCP session per request boundary** — per Temporal activity, per HTTP request, per recipe invocation. Never share a long-lived session across users; permissions are per key.
3. **Use the read-side tools only:** `search_knowledge`, `search_keyword`, `read`, `read_around`, `list_contents`, `find`, `get_info`, `view_chunk_image`, `get_organization_info`, `get_current_datetime`. See [MCP tool reference](mcp-tools.md).
4. **Copy `[chunk:<uuid>]` markers from `read()` output verbatim into your schema's citation field.** Don't synthesize UUIDs; CI rejects fabricated citations.
5. **Use a grounding-capable model.** `gpt-4o`, `claude-opus-4-x`, or stronger. `gpt-4o-mini` skips grounding and emits empty citations.

## Porting a flagship to your framework

Every flagship in `flagships/*/` follows this shape:

```
src/<module>/
  __main__.py     # CLI / entry point
  agent.py        # prompt + MCP wiring + Agent(output_type=Schema)
  schema.py       # pydantic models including Citation
  sample_inputs/  # default demo input
```

To port to another framework:

1. **Keep `schema.py` unchanged.** Pydantic models are framework-agnostic — every page on this wiki re-uses them as-is.
2. **Keep the system prompt unchanged.** It encodes the search→read→cite contract the model needs to follow regardless of runtime.
3. **Replace `agent.py`** with the framework-specific wiring (the per-framework pages each show ~30 lines).
4. **Keep `__main__.py` thin** — argparse, env, calls into your `draft_*()` function.

The 32 flagships shipped in this repo are pydantic-ai because that's our reference. **Any of them can run under any of the frameworks above** by swapping `agent.py`. Contributions of cross-framework ports of existing flagships are welcome — see [Writing a flagship](writing-a-flagship.md) and [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Things every framework must get right

- **Pass `KS_API_KEY` in env, not in tool arguments.**
- **Don't add a second MCP server.** The KS-only contract is what makes citations and permissions meaningful.
- **One MCP session per request boundary.** Don't share across users.
- **Temperature 0 (or near).** Grounding is brittle at high temperatures; agents start skipping `read()`.
- **Cap tool-call loops** (`max_turns` / `request_limit` / activity timeout). KS retrieval normally settles in ~10–20 calls; >40 means the agent is stuck.
- **Validate citations post-hoc.** Reject any `chunk_id` your code didn't actually see in a `read()` result. The frameworks page for each runtime shows where that gate lives (LangGraph review node, OpenAI guardrail, CrewAI reviewer agent, Temporal activity).

See [Troubleshooting](troubleshooting.md) for framework-specific errors.
