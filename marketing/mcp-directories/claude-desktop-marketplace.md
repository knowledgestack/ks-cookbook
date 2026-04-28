# Submission packet — Claude Desktop MCP Marketplace

**Submission URL:** https://github.com/anthropics/claude-desktop-mcp
**Submission format:** Tracked via `awesome-mcp-servers` and Anthropic's curated list. Submit via PR.


---

## Name

Knowledge Stack

## One-line description

Document intelligence MCP server — ingestion, RBAC, versioning, and citation-first retrieval for agents.

## Short description (≤ 280 chars)

Knowledge Stack — document intelligence layer for agents. Ingestion, chunking, RBAC, versioning, and citation tracking exposed as MCP tools (`search_knowledge`, `read`, `list_contents`, `read_around`, `find`, `get_info`, `view_chunk_image`, `get_organization_info`, `search_keyword`, `get_current_datetime`). Every read returns `[chunk:<uuid>]` markers so agent outputs cite exact source. 40+ open-source flagship agents in the cookbook spanning banking, legal, healthcare, insurance, government, energy, sales, and HR.

## Long description (markdown)

**Knowledge Stack** turns your document corpus into an agent-ready knowledge layer.

- **MCP-native** — `uvx knowledgestack-mcp` and you're plugged into Claude Desktop, Cursor, or any MCP host.
- **Citation-first** — every chunk read returns `[chunk:<uuid>]` markers; agent schemas reject outputs without them.
- **Multi-tenant + RBAC** — path-based permissions, OWNER/ADMIN/USER roles, per-tenant isolation.
- **Framework-agnostic** — works with LangChain, LangGraph, CrewAI, pydantic-ai, OpenAI Agents SDK, raw function calling.
- **40+ open-source flagship agents** in the [cookbook](https://github.com/knowledgestack/ks-cookbook) — credit memos, lease abstracts, prior-auth letters, FOIA responses, audit workpapers, NERC compliance evidence, and more.

**Install:** `uvx knowledgestack-mcp`
**SDKs:** `pip install ksapi` · `npm i @knowledge-stack/ksapi`
**Repo:** https://github.com/knowledgestack/ks-mcp
**Cookbook:** https://github.com/knowledgestack/ks-cookbook
**Docs:** https://docs.knowledgestack.ai


## Install command

```bash
uvx knowledgestack-mcp
```

## Claude Desktop config

```json
{
  "mcpServers": {
    "knowledgestack": {
      "command": "uvx",
      "args": ["knowledgestack-mcp"],
      "env": {
        "KS_API_KEY": "ks_...",
        "KS_BASE_URL": "https://api.knowledgestack.ai"
      }
    }
  }
}
```

## Required env

| Var | Required | Description |
|-----|----------|-------------|
| `KS_API_KEY` | yes | Get one free at https://knowledgestack.ai |
| `KS_BASE_URL` | no | Defaults to https://api.knowledgestack.ai |

## Tools exposed (read-only v1)

`search_knowledge`, `search_keyword`, `read`, `read_around`, `list_contents`, `find`, `get_info`, `view_chunk_image`, `get_organization_info`, `get_current_datetime`

## Tags

`rag`, `knowledge-base`, `document-ai`, `citations`, `multi-tenant`, `rbac`, `enterprise`

## License

MIT

## Maintainer

Knowledge Stack — https://knowledgestack.ai · hello@knowledgestack.ai
