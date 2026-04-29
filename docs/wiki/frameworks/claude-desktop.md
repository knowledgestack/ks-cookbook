# Knowledge Stack with Claude Desktop & Cursor

For end-user assistants — Claude Desktop, Cursor, Windsurf, any MCP-aware IDE — KS plugs in as an **MCP server in config**. No code, no agent framework. Your assistant gets tenant-scoped retrieval inside the chat UI.

This page is the right entry point if you don't want to build an agent at all and just want KS-backed answers in your editor or chat client.

## Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "knowledgestack": {
      "command": "uvx",
      "args": ["knowledgestack-mcp"],
      "env": {
        "KS_API_KEY": "sk-user-...",
        "KS_BASE_URL": "https://api.knowledgestack.ai"
      }
    }
  }
}
```

Restart Claude Desktop. You should see a 🔌 icon showing `knowledgestack` connected, and tool calls (`search_knowledge`, `read`, `list_contents`, …) available in the chat.

### Verify

In Claude Desktop, ask:

> "Use search_knowledge to find anything about MFA in our SOC 2 policy, then read it."

You'll see Claude call `search_knowledge`, then `read`, and quote `[chunk:<uuid>]` markers in its answer.

## Cursor

`~/.cursor/mcp.json` (or **Settings → MCP → Add server**):

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

Cursor's agent mode (Cmd-I) then has KS tools available — useful for "find the contract clause about renewals" while you're editing code that consumes that contract data.

## Windsurf, Cody, Continue.dev, Zed

Same JSON shape, different config path. Any MCP-aware client works; consult the client's MCP docs for the exact location.

## Ask-the-doc patterns that work well in chat

Some prompts that play well with the KS tool surface:

- **"Find every mention of X across our policies and quote them with citations."** — drives `search_knowledge` → `read` loops; chunk markers come through naturally.
- **"What does {doc} say about {topic}?"** — `find` + `read`.
- **"Walk me through the {section} of {doc}."** — `read` + `read_around` for context.
- **"Which folders do I have access to?"** — `list_contents` with no folder_id.
- **"What's in this image?"** — `view_chunk_image` if the corpus has chunks with images (e.g. CDC PPTX).

## Permissions

The `KS_API_KEY` in the config is the assistant's identity. If you put your own key there:

- The assistant can read every document **you** can read.
- Queries inherit your folder ACLs automatically.
- A teammate with a different key sees a different slice.

For shared machines, prefer per-user keys over a service-account key — otherwise everyone using that workstation gets your access.

## Multiple tenants

Need to switch between tenants (e.g. a personal cookbook tenant and your company tenant)? Add one entry per `KS_API_KEY`:

```json
{
  "mcpServers": {
    "ks-personal": { "command": "uvx", "args": ["knowledgestack-mcp"],
                     "env": { "KS_API_KEY": "sk-user-personal-..." } },
    "ks-company":  { "command": "uvx", "args": ["knowledgestack-mcp"],
                     "env": { "KS_API_KEY": "sk-user-company-..." } }
  }
}
```

Each shows up as its own toolset in the client.

## Gotchas

- **`uvx` must be on PATH.** GUI apps don't always inherit your shell PATH on macOS. If `uvx` isn't found, replace with the absolute path: `"/Users/you/.cargo/bin/uvx"` (or wherever `which uvx` reports).
- **API key in plaintext config.** The MCP config files are not encrypted. Treat them like `~/.aws/credentials` — restrict file permissions.
- **Restart after config changes.** Claude Desktop reads the file at launch only.
- **No code = no schema enforcement.** Chat responses are prose, not pydantic objects. For schema-enforced output, use one of the [agent framework integrations](../frameworks.md) instead.
