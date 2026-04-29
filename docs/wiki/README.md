# Knowledge Stack Cookbook — Developer Wiki

Developer-facing reference for building agents on top of Knowledge Stack.

These pages cover **how to use** Knowledge Stack from the client side — the MCP tool surface, framework integrations, and the cookbook's extension points. They deliberately do **not** document how the KS backend is implemented; for that, see the [Knowledge Stack product docs](https://docs.knowledgestack.ai).

## Pages

### Getting started

| Page | What's in it |
|---|---|
| [Overview](overview.md) | Why this repo exists, what KS manages, pipeline mental model, repo map. |
| [Quickstart](quickstart.md) | `git clone` → first recipe in ~5 min. Path A (shared tenant) and Path B (your own tenant). |
| [Connecting to Knowledge Stack](connecting.md) | API keys, base URLs, wiring the MCP server into your agent. |

### The cookbook, as a book

| Page | What's in it |
|---|---|
| [Cookbook book](book/README.md) | Every flagship and recipe README assembled into one navigable book — read every example without leaving the wiki. |
| ↳ [Flagships book](book/flagships.md) | 44 flagships, grouped by vertical, full READMEs inline. |
| ↳ [Recipes book](book/recipes.md) | 100+ recipes, alphabetized, full READMEs inline. |

### Building on top

| Page | What's in it |
|---|---|
| [Framework integrations](frameworks.md) | Hub: pick your framework. Every framework runs every flagship — see worked ports below. |
| ↳ [pydantic-ai](frameworks/pydantic-ai.md) · [LangChain](frameworks/langchain.md) · [LangGraph](frameworks/langgraph.md) · [CrewAI](frameworks/crewai.md) · [OpenAI Agents SDK](frameworks/openai-agents.md) · [Temporal](frameworks/temporal.md) · [Claude Desktop & Cursor](frameworks/claude-desktop.md) · [Custom MCP](frameworks/custom-mcp.md) | One worked example each — same flagship, ported. |
| [MCP tool reference](mcp-tools.md) | The ten read-only tools your agent is allowed to call, with argument and return shapes. |
| [Configuration](configuration.md) | Every environment variable and per-demo override. |
| [Seed data required](seed-data.md) | Which documents each flagship expects in your tenant, and how to seed them. |

### Contributing

| Page | What's in it |
|---|---|
| [Writing a flagship](writing-a-flagship.md) | File layout, prompt pattern, schema-constrained output, wiring a new `demo-<name>` target. |
| [Writing a recipe](writing-a-recipe.md) | The ≤100-LOC single-file pattern, frontmatter, `ks_mcp_session()`. |
| [Troubleshooting](troubleshooting.md) | Common errors when running flagships or connecting the MCP server. |

## If you're brand new

1. Read the root [README](../../README.md) — quick cover page.
2. Skim the [Overview](overview.md) for the mental model.
3. Follow the [Quickstart](quickstart.md) to get an API key and run your first recipe.
4. When you're ready to plug KS into your own stack, jump to [Framework integrations](frameworks.md).
