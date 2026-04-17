# Knowledge Stack Cookbook — Developer Wiki

Developer-facing reference for building agents on top of Knowledge Stack.

These pages cover **how to use** Knowledge Stack from the client side — API keys, the MCP tool surface, and the cookbook's extension points. They deliberately do **not** document how the Knowledge Stack backend is implemented; for that, see the Knowledge Stack product docs.

## Pages

| Page | What's in it |
|---|---|
| [Connecting to Knowledge Stack](connecting.md) | Get an API key, point at the right environment, authenticate the MCP server from your agent. |
| [MCP tool reference](mcp-tools.md) | The read-only tool surface your agent is allowed to call, with argument and return shapes. |
| [Seed data required](seed-data.md) | Which documents each flagship expects in your tenant, and the seed script to populate them. |
| [Configuration](configuration.md) | Every environment variable and per-demo override the cookbook understands. |
| [Writing a flagship](writing-a-flagship.md) | File layout, prompt pattern, schema-constrained output, wiring a new `demo-<name>` target. |
| [Writing a recipe](writing-a-recipe.md) | The ≤100-LOC single-file pattern, frontmatter, `ks_mcp_session()`. |
| [Troubleshooting](troubleshooting.md) | Common errors when running flagships or connecting the MCP server. |

## If you're brand new

1. Read the root [README](../../README.md) for a 5-minute overview.
2. Follow [Connecting to Knowledge Stack](connecting.md) to get an API key and run your first demo.
3. Skim [Writing a flagship](writing-a-flagship.md) to see the pattern every demo follows.
