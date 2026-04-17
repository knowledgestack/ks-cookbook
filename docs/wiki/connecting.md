# Connecting to Knowledge Stack

Every flagship and recipe in this repo talks to Knowledge Stack through the **`knowledgestack-mcp`** server. You never call the Knowledge Stack HTTP API directly — the MCP server is the stable, versioned surface for agents.

This page covers everything a developer needs to get an agent talking to their Knowledge Stack tenant.

## What you need

- A **Knowledge Stack API key** scoped to the user or service account whose permissions your agent should inherit.
- The **base URL** for your Knowledge Stack environment (production SaaS or your own deployment).
- An **LLM API key** (OpenAI or Anthropic) — the cookbook's example agents use one of these, but the MCP server itself is LLM-agnostic.

## 1. Get an API key

Issue a key from the Knowledge Stack dashboard. The key inherits the permissions of the user it's issued for — a KYC analyst's key will see a different slice of the corpus than a compliance lead's. This is intentional: it's how the cookbook demonstrates permission-aware retrieval without any special plumbing.

Keys look like `sk-user-...`. Treat them like any other credential.

## 2. Point at the right environment

Set these in `.env` at the repo root:

```env
KS_API_KEY=sk-user-...
KS_BASE_URL=https://api.knowledgestack.ai   # prod SaaS; override for staging or self-hosted
```

`KS_BASE_URL` defaults to the production SaaS and can be omitted for normal use.

## 3. Install the MCP server

`make setup` installs `knowledgestack-mcp` into the workspace venv at `.venv/bin/ks-mcp`. If you want the published release instead, use `uvx`:

```bash
uvx knowledgestack-mcp --help
```

## 4. Wire it into your agent

### pydantic-ai (stdio)

```python
from pydantic_ai.mcp import MCPServerStdio

mcp = MCPServerStdio(
    command="uvx",
    args=["knowledgestack-mcp"],
    env={"KS_API_KEY": os.environ["KS_API_KEY"],
         "KS_BASE_URL": os.environ.get("KS_BASE_URL", "")},
)
agent = Agent(model="openai:gpt-4o", mcp_servers=[mcp], output_type=MySchema)
async with agent.run_mcp_servers():
    result = await agent.run("...")
```

Every flagship under `flagships/*/agent.py` follows this shape.

### Claude Desktop / Cursor (stdio)

Add to your MCP config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

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

### LangGraph, OpenAI Agents SDK, raw clients

Any MCP-speaking client works. Spawn `knowledgestack-mcp` over **stdio** (the default) or run it as a **Streamable HTTP** server:

```bash
uvx knowledgestack-mcp --http --port 8765
```

Then point your client at `http://localhost:8765`.

### From a recipe (shared helper)

Recipes use the shared wrapper instead of constructing `MCPServerStdio` by hand:

```python
from recipes._shared.mcp_client import ks_mcp_session

async with ks_mcp_session() as session:
    result = await session.call_tool("list_contents", {"folder_id": folder_id})
```

The wrapper reads `KS_MCP_COMMAND` / `KS_MCP_ARGS` from the environment so you can swap the server binary without touching recipe code.

## 5. Verify the connection

Two quick checks:

```bash
# The MCP Inspector lets you click through every tool with a real API key.
npx @modelcontextprotocol/inspector uvx knowledgestack-mcp

# Or run the lightest flagship end-to-end.
make demo-handbook-qa QUESTION="smoke test"
```

If `get_organization_info` returns your tenant name, the key and base URL are wired up correctly.

## How permissions work (client-side view)

You don't configure permissions in your agent. The API key you use determines which folders, documents, and chunks every MCP call can see. If a user can't see a document in the KS UI, no amount of clever prompting will let an agent using their key read it either.

This is the property the cookbook relies on: the same flagship code produces different, correct outputs for different users simply because they have different keys.

## What not to do

- **Don't hit the Knowledge Stack HTTP API directly from flagships or recipes.** The MCP contract is the supported surface; direct API calls will break under future backend changes.
- **Don't add a second MCP server.** The KS-only contract is enforced on contribution. If you need another data source, wrap it in a tool exposed by `knowledgestack-mcp`.
- **Don't commit `.env`.** The repo ignores it; keep API keys out of source.
