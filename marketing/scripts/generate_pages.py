"""Generate Tier-1 marketing pages from a single source of truth.

Run from repo root:
    python marketing/scripts/generate_pages.py

Emits:
- marketing/seo-pages/<slug>.md         (one per flagship)
- marketing/comparisons/*.md            (5 alt pages)
- marketing/mcp-directories/*.md        (submission packets)
- marketing/awesome-prs/*.md            (PR-ready snippets)

Pages are static markdown that the docs site (Mintlify) or marketing site
can ingest verbatim — no rendering layer needed.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FLAGSHIPS_DIR = ROOT / "flagships"
OUT = ROOT / "marketing"


def slug_to_title(slug: str) -> str:
    return " ".join(w.capitalize() for w in slug.split("_"))


def read_description(slug: str) -> str:
    pyproject = FLAGSHIPS_DIR / slug / "pyproject.toml"
    if not pyproject.exists():
        return ""
    for line in pyproject.read_text().splitlines():
        m = re.match(r'description\s*=\s*"([^"]+)"', line)
        if m:
            return m.group(1)
    return ""


def vertical_from_description(desc: str) -> str:
    desc_l = desc.lower()
    for v in (
        "banking",
        "legal",
        "healthcare",
        "pharma",
        "finance",
        "accounting",
        "insurance",
        "real estate",
        "government",
        "energy",
        "construction",
        "sales",
        "tax",
        "hr",
    ):
        if v in desc_l:
            return v.title()
    return "General"


SEO_TEMPLATE = """---
title: "{title} agent — grounded in your docs, with citations"
description: "{description}"
keywords: ["{slug_kw}", "{vertical_l} agent", "{vertical_l} RAG", "document AI", "MCP"]
---

# {title}

{description}

Built on **Knowledge Stack** — the document intelligence layer for agents. Every output cites the exact `[chunk:<uuid>]` it came from, so reviewers can trace any sentence back to source.

## What it does

- Connects to your `knowledgestack-mcp` server over stdio.
- Enumerates the `{vertical_l}` corpus folder, reads relevant chunks, and produces a structured pydantic output.
- Writes a Word/Markdown/Excel artifact your team can ship to a customer, regulator, or internal reviewer.
- Refuses to fabricate citations: every `chunk_id` is copied verbatim from `read` tool output (CI-enforced).

## Try it in 60 seconds

```bash
git clone https://github.com/knowledgestack/ks-cookbook
cd ks-cookbook
echo "KS_API_KEY=ks_..." > .env
echo "OPENAI_API_KEY=sk-..." >> .env
make setup
make demo-{slug_kebab}
```

Output: a cited `.md` / `.docx` / `.xlsx` you can hand to a reviewer.

## SDKs

- **Python:** `pip install ksapi`
- **TypeScript:** `npm i @knowledge-stack/ksapi`
- **MCP:** `uvx knowledgestack-mcp` (works in Claude Desktop, Cursor, any MCP host)

## Why citations matter for {vertical_l}

In {vertical_l}, an unsourced AI answer is a liability. Knowledge Stack threads `[chunk:<uuid>]` markers through every read, and the schema rejects outputs that lack them. That's the difference between a demo and a control your auditors accept.

## Source

- Flagship: [`flagships/{slug_path}/`](https://github.com/knowledgestack/ks-cookbook/tree/main/flagships/{slug_path})
- Get a free API key: [knowledgestack.ai](https://knowledgestack.ai)
- Docs: [docs.knowledgestack.ai](https://docs.knowledgestack.ai)
- Discord: [join](https://discord.gg/McHmxUeS)
"""


def write_seo_pages() -> int:
    out_dir = OUT / "seo-pages"
    out_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for d in sorted(FLAGSHIPS_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        slug = d.name
        desc = read_description(slug)
        if not desc:
            continue
        vertical = vertical_from_description(desc)
        page = SEO_TEMPLATE.format(
            title=slug_to_title(slug),
            description=desc.replace('"', "'"),
            slug_kw=slug.replace("_", " "),
            slug_kebab=slug.replace("_", "-"),
            slug_path=slug,
            vertical_l=vertical,
        )
        (out_dir / f"{slug}.md").write_text(page)
        n += 1
    return n


COMPARISONS = [
    {
        "slug": "vs-llamacloud",
        "competitor": "LlamaCloud",
        "their_pitch": "Hosted parsing + indexing for LlamaIndex apps.",
        "our_edge": [
            "**MCP-native.** Knowledge Stack ships a stable MCP server out of the box. LlamaCloud requires you to wrap their REST API yourself before it works in Claude Desktop or Cursor.",
            "**Citations are the contract, not a feature.** Every chunk read returns `[chunk:<uuid>]` markers and the schema rejects outputs without them. CI enforces it across 40+ flagship agents.",
            "**Multi-tenant + RBAC built in.** Per-tenant isolation, path-based permissions, OWNER/ADMIN/USER roles — not a future roadmap item.",
            "**Framework-agnostic.** Works with LangChain, LangGraph, CrewAI, pydantic-ai, OpenAI Agents SDK, raw function calling. LlamaCloud is best inside LlamaIndex.",
        ],
    },
    {
        "slug": "vs-unstructured",
        "competitor": "Unstructured.io",
        "their_pitch": "Document parsing API for any doc type.",
        "our_edge": [
            "**End-to-end, not just parsing.** Knowledge Stack handles ingestion, chunking, versioning, permissions, retrieval, *and* citation tracking. Unstructured stops at parsed JSON.",
            "**MCP server included.** Plug into any agent host without writing glue code.",
            "**Permission-aware retrieval.** RBAC propagates through to chunk-level access — Unstructured leaves authz to you.",
            "**40+ production-style agents** in the open-source cookbook to copy from.",
        ],
    },
    {
        "slug": "vs-ragie",
        "competitor": "Ragie",
        "their_pitch": "Hosted RAG-as-a-service.",
        "our_edge": [
            "**Open-source cookbook.** 40+ flagships, 100+ recipes, MIT-licensed. Clone, modify, ship.",
            "**MCP-first.** Same server works in Claude Desktop, Cursor, and your production agent.",
            "**Strict citation contract.** `[chunk:<uuid>]` markers verified in CI — no silent hallucinations.",
            "**Self-host or hosted.** Same SDKs, same MCP surface, your choice.",
        ],
    },
    {
        "slug": "vs-vectara",
        "competitor": "Vectara",
        "their_pitch": "Managed semantic search + grounded generation.",
        "our_edge": [
            "**Agent-shaped, not query-shaped.** Knowledge Stack exposes `list_contents` / `read` / `read_around` — the primitives an agent actually uses to navigate a corpus, not just `search`.",
            "**MCP server, not a proprietary API.** Standard protocol, swap hosts freely.",
            "**Cookbook of working agents** in banking, legal, healthcare, insurance, government — copy and ship.",
            "**Versioning + lineage** so you can roll back a corpus without re-indexing from scratch.",
        ],
    },
    {
        "slug": "vs-reducto",
        "competitor": "Reducto",
        "their_pitch": "High-fidelity document parsing for finance/legal.",
        "our_edge": [
            "**Reducto parses; Knowledge Stack runs the agent.** Use Reducto for parsing if you like — pipe its output into Knowledge Stack and get retrieval, RBAC, citations, and an MCP surface for free.",
            "**40+ vertical agents** including credit memos, lease abstracts, prior-auth letters, FOIA responses — already wired up.",
            "**MCP-native** so the same agent runs in Claude Desktop and in production.",
            "**Free tier + open-source cookbook.** Try every flagship before you talk to sales.",
        ],
    },
]


COMPARISON_TEMPLATE = """---
title: "Knowledge Stack vs {competitor} — which RAG infra should you build on?"
description: "Knowledge Stack is the MCP-native, citation-first alternative to {competitor}. 40+ open-source flagship agents, multi-tenant RBAC, and SDKs that work out of the box."
keywords: ["{competitor_l} alternative", "{competitor_l} vs", "RAG infrastructure", "document AI", "MCP"]
---

# Knowledge Stack vs {competitor}

> {their_pitch}

Knowledge Stack is the **MCP-native, citation-first** alternative — built so a single server backs both your Claude Desktop / Cursor workflow *and* your production agents.

## Why teams pick Knowledge Stack over {competitor}

{edges}

## Out-of-the-box developer experience

```bash
# Python
pip install ksapi

# TypeScript
npm i @knowledge-stack/ksapi

# MCP (Claude Desktop / Cursor / any MCP host)
uvx knowledgestack-mcp
```

Then clone the [cookbook](https://github.com/knowledgestack/ks-cookbook) and run `make demo-credit-memo` (or any of 40+ flagships) — cited output in under a minute.

## See it for yourself

- **Cookbook:** [github.com/knowledgestack/ks-cookbook](https://github.com/knowledgestack/ks-cookbook)
- **Docs:** [docs.knowledgestack.ai](https://docs.knowledgestack.ai)
- **Free API key:** [knowledgestack.ai](https://knowledgestack.ai) — no credit card.
- **Discord:** [join](https://discord.gg/McHmxUeS)

*Disclaimer: comparison reflects publicly documented capabilities of {competitor} at time of writing. Corrections welcome — open a PR on `ks-cookbook`.*
"""


def write_comparisons() -> int:
    out_dir = OUT / "comparisons"
    out_dir.mkdir(parents=True, exist_ok=True)
    for c in COMPARISONS:
        edges = "\n".join(f"- {e}" for e in c["our_edge"])
        page = COMPARISON_TEMPLATE.format(
            competitor=c["competitor"],
            competitor_l=c["competitor"].lower(),
            their_pitch=c["their_pitch"],
            edges=edges,
        )
        (out_dir / f"{c['slug']}.md").write_text(page)
    return len(COMPARISONS)


MCP_DIRECTORIES = [
    {
        "slug": "smithery",
        "name": "Smithery (smithery.ai)",
        "url": "https://smithery.ai/new",
        "format": "GitHub repo URL + smithery.yaml in repo root.",
        "extra": "Add `smithery.yaml` to `ks-mcp` repo root with `startCommand: uvx knowledgestack-mcp` and config schema for `KS_API_KEY`.",
    },
    {
        "slug": "mcp-so",
        "name": "mcp.so",
        "url": "https://mcp.so/submit",
        "format": "Web form: name, repo URL, description, tags, install command.",
        "extra": None,
    },
    {
        "slug": "glama-ai",
        "name": "Glama (glama.ai/mcp)",
        "url": "https://glama.ai/mcp/servers",
        "format": "Auto-indexed from GitHub topic `mcp` + `mcp-server`. Add both topics to `ks-mcp` repo settings.",
        "extra": "Add a `claude-mcp` topic too — Glama uses it as a quality signal.",
    },
    {
        "slug": "mcp-get",
        "name": "mcp-get registry",
        "url": "https://github.com/michaellatman/mcp-get",
        "format": "PR adding entry to `packages.json` with name, command, args, env schema.",
        "extra": None,
    },
    {
        "slug": "cursor-directory",
        "name": "Cursor MCP Directory",
        "url": "https://cursor.directory/mcp",
        "format": "PR to `pontusab/cursor.directory` with new MCP entry.",
        "extra": "Provide one-click install deeplink: `cursor://anysphere.cursor-deeplink/mcp/install?name=knowledgestack&config=<base64>`.",
    },
    {
        "slug": "claude-desktop-marketplace",
        "name": "Claude Desktop MCP Marketplace",
        "url": "https://github.com/anthropics/claude-desktop-mcp",
        "format": "Tracked via `awesome-mcp-servers` and Anthropic's curated list. Submit via PR.",
        "extra": None,
    },
    {
        "slug": "awesome-mcp-servers",
        "name": "awesome-mcp-servers",
        "url": "https://github.com/punkpeye/awesome-mcp-servers",
        "format": "PR adding bullet under appropriate category (Knowledge & Memory).",
        "extra": None,
    },
]


SHORT_BLURB = (
    "Knowledge Stack — document intelligence layer for agents. "
    "Ingestion, chunking, RBAC, versioning, and citation tracking exposed as MCP tools "
    "(`search_knowledge`, `read`, `list_contents`, `read_around`, `find`, `get_info`, "
    "`view_chunk_image`, `get_organization_info`, `search_keyword`, `get_current_datetime`). "
    "Every read returns `[chunk:<uuid>]` markers so agent outputs cite exact source. "
    "40+ open-source flagship agents in the cookbook spanning banking, legal, healthcare, "
    "insurance, government, energy, sales, and HR."
)

LONG_BLURB = """**Knowledge Stack** turns your document corpus into an agent-ready knowledge layer.

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
"""

CLAUDE_DESKTOP_CONFIG = """```json
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
```"""


MCP_DIR_TEMPLATE = """# Submission packet — {name}

**Submission URL:** {url}
**Submission format:** {format}
{extra_block}

---

## Name

Knowledge Stack

## One-line description

Document intelligence MCP server — ingestion, RBAC, versioning, and citation-first retrieval for agents.

## Short description (≤ 280 chars)

{short_blurb}

## Long description (markdown)

{long_blurb}

## Install command

```bash
uvx knowledgestack-mcp
```

## Claude Desktop config

{claude_desktop_config}

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
"""


def write_mcp_directories() -> int:
    out_dir = OUT / "mcp-directories"
    out_dir.mkdir(parents=True, exist_ok=True)
    for d in MCP_DIRECTORIES:
        extra_block = f"\n**Note:** {d['extra']}" if d["extra"] else ""
        page = MCP_DIR_TEMPLATE.format(
            name=d["name"],
            url=d["url"],
            format=d["format"],
            extra_block=extra_block,
            short_blurb=SHORT_BLURB,
            long_blurb=LONG_BLURB,
            claude_desktop_config=CLAUDE_DESKTOP_CONFIG,
        )
        (out_dir / f"{d['slug']}.md").write_text(page)
    return len(MCP_DIRECTORIES)


AWESOME_LISTS = [
    {
        "slug": "awesome-langchain",
        "list": "kyrolabs/awesome-langchain",
        "section": "Tools / Knowledge bases",
        "bullet": "- [Knowledge Stack](https://github.com/knowledgestack/ks-cookbook) — Document intelligence layer with citation-first retrieval. MCP server + Python/TS SDKs + 40 flagship agents using LangChain & LangGraph.",
    },
    {
        "slug": "awesome-langgraph",
        "list": "von-development/awesome-LangGraph",
        "section": "Examples",
        "bullet": "- [ks-cookbook](https://github.com/knowledgestack/ks-cookbook) — 40+ production-style LangGraph agents (credit memos, audit workpapers, NERC compliance, claims adjudication) grounded via MCP with `[chunk:<uuid>]` citations.",
    },
    {
        "slug": "awesome-crewai",
        "list": "crewAIInc/awesome-crewai",
        "section": "Real-world examples",
        "bullet": "- [Knowledge Stack cookbook](https://github.com/knowledgestack/ks-cookbook) — CrewAI-compatible RAG flagships with strict citation contracts.",
    },
    {
        "slug": "awesome-mcp-servers",
        "list": "punkpeye/awesome-mcp-servers",
        "section": "Knowledge & Memory",
        "bullet": "- [knowledgestack/ks-mcp](https://github.com/knowledgestack/ks-mcp) — Document intelligence: RBAC-aware ingestion, versioning, citation-first retrieval. Free tier. `uvx knowledgestack-mcp`.",
    },
    {
        "slug": "awesome-pydantic-ai",
        "list": "pydantic/pydantic-ai (examples directory)",
        "section": "Community examples",
        "bullet": "- [ks-cookbook](https://github.com/knowledgestack/ks-cookbook) — pydantic-ai flagships (research-brief, clinical-trial-eligibility, NERC compliance) with strongly-typed cited outputs.",
    },
    {
        "slug": "openai-agents-python-examples",
        "list": "openai/openai-agents-python (examples)",
        "section": "Third-party MCP integrations",
        "bullet": "- [Knowledge Stack](https://github.com/knowledgestack/ks-cookbook) — MCP server + 40 cited-output flagships compatible with the Agents SDK.",
    },
]


AWESOME_PR_TEMPLATE = """# PR — {list}

**Section to add to:** `{section}`

**One-line addition (copy-paste):**

{bullet}

---

## PR description (paste into PR body)

Adding Knowledge Stack to the {section} section.

**What it is:** Document intelligence layer for agents. MCP-native, citation-first, multi-tenant. The cookbook ships 40+ production-style flagship agents that use {framework_hint}.

**Why it fits this list:** {fit}

**Repos:**
- Cookbook (open-source, MIT): https://github.com/knowledgestack/ks-cookbook
- MCP server: https://github.com/knowledgestack/ks-mcp
- Python SDK (PyPI `ksapi`): https://github.com/knowledgestack/ks-sdk-python
- TypeScript SDK (`@knowledge-stack/ksapi`): https://github.com/knowledgestack/ks-sdk-ts
- Docs: https://docs.knowledgestack.ai

Happy to adjust placement, wording, or section per your preferences.
"""


def write_awesome_prs() -> int:
    out_dir = OUT / "awesome-prs"
    out_dir.mkdir(parents=True, exist_ok=True)
    for a in AWESOME_LISTS:
        framework_hint = {
            "awesome-langchain": "LangChain and LangGraph",
            "awesome-langgraph": "LangGraph (ReAct + state-machine patterns)",
            "awesome-crewai": "CrewAI (multi-agent orchestration)",
            "awesome-mcp-servers": "the Model Context Protocol",
            "awesome-pydantic-ai": "pydantic-ai for typed agent outputs",
            "openai-agents-python-examples": "the OpenAI Agents SDK",
        }.get(a["slug"], "the listed framework")
        fit = (
            "Real production patterns with verifiable citations — not toy demos. "
            "Every flagship calls MCP tools and emits `[chunk:<uuid>]` markers, CI-enforced."
        )
        page = AWESOME_PR_TEMPLATE.format(
            list=a["list"],
            section=a["section"],
            bullet=a["bullet"],
            framework_hint=framework_hint,
            fit=fit,
        )
        (out_dir / f"{a['slug']}.md").write_text(page)
    return len(AWESOME_LISTS)


def main() -> None:
    n_seo = write_seo_pages()
    n_cmp = write_comparisons()
    n_mcp = write_mcp_directories()
    n_pr = write_awesome_prs()
    print(f"SEO pages:       {n_seo}")
    print(f"Comparisons:     {n_cmp}")
    print(f"MCP directories: {n_mcp}")
    print(f"Awesome PRs:     {n_pr}")


if __name__ == "__main__":
    main()
