# Knowledge Stack — Tier 1 Developer Traction Campaign

Goal: maximize qualified developer signups per dollar by turning the cookbook + MCP server into the acquisition engine. Every artifact below is free to ship.

## What's in this directory

| Path | Count | Purpose |
|------|------:|---------|
| [`seo-pages/`](./seo-pages) | 44 | One programmatic-SEO page per flagship — long-tail intent (`"credit memo agent"`, `"lease abstract LLM"`, `"NERC compliance evidence"`). Drop into `ks-docs` Mintlify or the marketing site. |
| [`comparisons/`](./comparisons) | 5 | Alternative pages targeting `LlamaCloud`, `Unstructured.io`, `Ragie`, `Vectara`, `Reducto` evaluators. |
| [`mcp-directories/`](./mcp-directories) | 7 | Submission packets for every MCP directory. Each file has the exact copy + install command + Claude Desktop config to paste. |
| [`awesome-prs/`](./awesome-prs) | 6 | One-line awesome-list additions + PR description for LangChain, LangGraph, CrewAI, MCP servers, pydantic-ai, OpenAI Agents SDK. |
| [`scripts/generate_pages.py`](./scripts/generate_pages.py) | 1 | Regenerates everything from flagship pyproject.toml descriptions. Re-run after adding flagships. |

Total: **62 ready-to-ship marketing artifacts**, generated from the cookbook itself.

## Execution order (Tier 1)

### Day 1 — MCP directories (highest ROI per hour)

For each file in `mcp-directories/`, follow the linked submission URL and paste the contents. They're already formatted to fit each directory's expected fields.

- [ ] [Smithery](./mcp-directories/smithery.md) — also add `smithery.yaml` to `ks-mcp` repo root
- [ ] [mcp.so](./mcp-directories/mcp-so.md)
- [ ] [Glama](./mcp-directories/glama-ai.md) — add GitHub topics `mcp`, `mcp-server`, `claude-mcp` to `ks-mcp`
- [ ] [mcp-get](./mcp-directories/mcp-get.md) — open PR
- [ ] [Cursor MCP Directory](./mcp-directories/cursor-directory.md) — open PR
- [ ] [Claude Desktop Marketplace](./mcp-directories/claude-desktop-marketplace.md)
- [ ] [awesome-mcp-servers](./mcp-directories/awesome-mcp-servers.md) — open PR

### Day 2 — Programmatic SEO

- [ ] Drop `seo-pages/*.md` into `ks-docs` under `/use-cases/<slug>` (Mintlify auto-renders frontmatter).
- [ ] Add a `/use-cases` index page listing all 44.
- [ ] Submit updated sitemap to Google Search Console + Bing Webmaster.
- [ ] Internal-link from each page to: SDK quickstart, signup, Discord.

### Day 3 — Comparisons

- [ ] Publish `comparisons/*.md` under `/compare/<slug>` on the marketing site.
- [ ] Link from `/pricing` (high-intent visitors look for alternatives).
- [ ] Add to sitemap.

### Day 4 — Awesome-list PRs

For each file in `awesome-prs/`, fork the target repo, add the bullet to the indicated section, open a PR with the provided description.

- [ ] LangChain → [`awesome-prs/awesome-langchain.md`](./awesome-prs/awesome-langchain.md)
- [ ] LangGraph → [`awesome-prs/awesome-langgraph.md`](./awesome-prs/awesome-langgraph.md)
- [ ] CrewAI → [`awesome-prs/awesome-crewai.md`](./awesome-prs/awesome-crewai.md)
- [ ] awesome-mcp-servers → [`awesome-prs/awesome-mcp-servers.md`](./awesome-prs/awesome-mcp-servers.md)
- [ ] pydantic-ai → [`awesome-prs/awesome-pydantic-ai.md`](./awesome-prs/awesome-pydantic-ai.md)
- [ ] OpenAI Agents SDK → [`awesome-prs/openai-agents-python-examples.md`](./awesome-prs/openai-agents-python-examples.md)

## Out-of-the-box readiness checklist

Before driving traffic, verify a cold dev reaches a cited output in <5 minutes:

- [ ] `pip install ksapi` works from a clean venv (latest version on PyPI)
- [ ] `npm i @knowledge-stack/ksapi` works (latest version on npm, matches backend OpenAPI)
- [ ] `uvx knowledgestack-mcp` runs with zero flags; clear error if `KS_API_KEY` missing
- [ ] One-click Claude Desktop config block in `ks-mcp` README (use [the snippet from any MCP-directory packet](./mcp-directories/smithery.md))
- [ ] Cursor one-click install deeplink in `ks-mcp` README
- [ ] Free-tier API key signup is **<60 seconds, no credit card**
- [ ] Default seeded corpus (`ab926019-ac7a-579f-bfda-6c52a13c5f41`) accessible on every new key
- [ ] `make demo-credit-memo` runs on a fresh clone in a clean Docker
- [ ] `ks-docs` has dedicated MCP page + SDK quickstart, ranks for `"knowledge stack mcp"`
- [ ] All five public repos (`ks-cookbook`, `ks-mcp`, `ks-sdk-python`, `ks-sdk-ts`, `ks-docs`) have green CI, MIT license, `CONTRIBUTING.md`, issue templates, Discord link in About
- [ ] `llms.txt` published on knowledgestack.ai

## Regenerating

After adding a flagship or recipe:

```bash
python marketing/scripts/generate_pages.py
```

The generator reads `flagships/*/pyproject.toml` `description` fields as the source of truth, so improving descriptions auto-improves SEO copy.
