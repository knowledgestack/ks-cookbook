# Knowledge Stack Cookbook

Build agents on top of [Knowledge Stack](https://knowledgestack.ai) from any framework — **pydantic-ai**, **LangGraph**, **OpenAI Agents SDK**, **Claude Desktop**, **Cursor** — via one MCP server and one API key.

This repo exists to help humans and coding agents understand **KS as a service**
quickly, then ship production-grade, grounded agents fast.

> Not affiliated with your production KS deployment. Reference implementations; review before shipping.

## Quickstart (60 seconds)

```bash
git clone https://github.com/knowledgestack/cookbook knowledgestack-cookbook
cd knowledgestack-cookbook

cp .env.example .env
# edit .env — fill in KS_API_KEY and OPENAI_API_KEY (or ANTHROPIC_API_KEY)

make setup      # one-time: installs deps + verifies .env
make demo-csv   # runs CSV enrichment end-to-end
make demo-research TOPIC="CRISPR off-target effects"
```

That's it. No other exports, no shell gymnastics.

## Purpose (for agents)

Use this repo as a KS onboarding system:

- Learn the KS MCP surface once (10 read-side tools).
- Reuse the same retrieval/grounding contract across any framework.
- Copy working agent patterns from recipes and flagships.
- Scale to 100+ agents without changing the enterprise data-access boundary.

The invariant is simple: **MCP access is KS-only (`knowledgestack-mcp`)**.

## What you get

- `enriched.csv` — the input CSV (`flagships/csv_enrichment/sample_inputs/customers.csv` by default) with a new `research_summary` column filled in by a LangGraph agent grounded in your KS tenant.
- `brief.docx` — a cited research brief from your KS tenant using a pydantic-ai agent.
- `filled.xlsx` — the Texas DPS public CAIQ v4.0.2 XLSX with 5 (configurable) rows answered with real `[chunk:<uuid>]` citations into your policy corpus.
- 8 one-file recipes under [`recipes/`](recipes/) covering real B2B pain (policy Q&A, vendor security review, incident post-mortem, SDLC checklist, onboarding checklist, permission-aware retrieval, LlamaIndex RAG, compliance questionnaire). Each ≤100 LOC, each uses a different framework. See [`recipes/INDEX.md`](recipes/INDEX.md).

## The design principle

**Flexibility, maintainability, quick time-to-market — with enterprise-grade trust.**

Agent frameworks move fast; enterprise data controls don't. KS splits the two:

```
              Identity (upstream)          Permissions (KS)
              ┌──────────────────┐        ┌──────────────────┐
 end-user ────▶ Okta / Azure AD  │──key──▶│ Knowledge Stack  │──filtered docs──▶ agent
              └──────────────────┘        └──────────────────┘
                     who                    what they can read
```

| Layer | Handled by | Not handled by |
|---|---|---|
| Login / SSO / MFA | Your IdP (Auth0, Azure AD, Google) | ❌ not KS |
| Per-user, per-folder, per-version permission enforcement | **✅ KS** | framework retrievers |
| Agent loop / tool-calling / framework glue | Your choice (multiple frameworks shown) | not locked |

Your agent code stays framework-flexible (pydantic-ai today, LangGraph tomorrow, LlamaIndex next quarter) but the data-access story stays identical and enterprise-safe because it's enforced in KS, not in whatever retriever your agent framework ships this week.

See [`recipes/permission_aware_retrieval/`](recipes/permission_aware_retrieval/) for the demo that makes it concrete — two end-users, same agent code, different documents returned, zero lines of permission logic in the developer's code.

## Commands

```
make setup          First-time setup (installs deps, validates .env)
make demo-csv       Run the CSV enrichment demo
make demo-research  Run the research-brief demo
make demo           Run both demos
make test           Unit tests (no live KS needed)
make lint           Ruff across the workspace
make clean          Remove generated artifacts
```

## Override inputs

```bash
make demo-csv IN=./my-leads.csv OUT=./my-leads-enriched.csv
make demo-research TOPIC="the state of post-quantum crypto"
```

## What's in the box

```
mcp-python/                 # `knowledgestack-mcp` — FastMCP server, 10 read-side tools
flagships/
  research_brief/           # pydantic-ai: topic → cited .docx
  csv_enrichment/           # LangGraph: CSV rows → enriched CSV
```

## Tools exposed (via `knowledgestack-mcp`)

These are the only MCP tools used in this repository:

| Tool | Purpose |
|---|---|
| `search_knowledge` | Semantic chunk search. |
| `search_keyword` | BM25 chunk search. |
| `read` / `read_around` | Fetch document / section / chunk text (+ neighbours). |
| `list_contents` / `find` / `get_info` | Navigate the folder tree. |
| `view_chunk_image` | Pull image bytes for IMAGE-type chunks. |
| `get_organization_info` / `get_current_datetime` | Tenant metadata + local time. |

Writes are intentionally not in v1 — the product is *grounded retrieval*, not "we let agents mutate your KB remotely."

## KS-only contract

- Use only the `knowledgestack` MCP server in recipes/flagships.
- Do not add secondary MCP servers to recipes/flagships.
- Ground every output in KS retrieval with chunk citations.

Agent context for this contract lives under [`.serena/`](.serena/README.md).

## Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "knowledgestack": {
      "command": "uvx",
      "args": ["knowledgestack-mcp"],
      "env": { "KS_API_KEY": "sk-user-..." }
    }
  }
}
```

## Security

- `.env` is gitignored. Never commit keys.
- Trial keys issued from the public demo tenant are read-only (enforced by `PathPermission` + `TENANT_READONLY_IDS`).
- A 402 from any tool means daily quota is exhausted — stop the loop.

## License

MIT.
