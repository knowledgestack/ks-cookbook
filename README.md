# Knowledge Stack Cookbook

**Build enterprise agents in minutes, not months.** 32 industry demos across banking, legal, accounting, healthcare, insurance, real estate, sales, pharma, energy, and government — each grounded in real data with verifiable citations.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Flagships](https://img.shields.io/badge/flagships-32-green)]()

---

## Get started in 60 seconds

### Step 1: Get your Knowledge Stack API key

1. Sign in to your KS tenant at **https://app.knowledgestack.ai**
2. Go to **Settings → API Keys**
3. Click **Create API Key** → copy the `sk-user-...` key (shown once)

> **Don't have a KS account?** [Sign up for a free trial](https://knowledgestack.ai) or [contact us](mailto:hello@knowledgestack.ai) for a demo tenant pre-loaded with sample data.

### Step 2: Clone and configure

```bash
git clone https://github.com/knowledgestack/ks-cookbook.git
cd ks-cookbook

cp .env.example .env
```

Edit `.env` — fill in two values:

```env
KS_API_KEY=sk-user-paste-your-key-here
OPENAI_API_KEY=sk-proj-paste-your-openai-key-here
```

### Step 3: Run your first demo

```bash
make setup          # one-time: installs dependencies, validates .env
make demo-credit-memo   # banking: draft a credit memo with 9 cited risk factors
```

That's it. Open `credit-memo.md` — every claim cites a real document chunk you can trace back to your KS tenant.

### Step 4: Try more demos

```bash
make demo-compliance          # auto-fill a CAIQ security questionnaire
make demo-contract-obligations  # extract 18 obligations from an MSA
make demo-rev-rec-memo        # ASC 606 5-step revenue recognition analysis
make demo-prior-auth          # draft a clinical prior-auth letter
make demo-earnings-risk       # 10-K risk-flag analyst memo (real SEC filing)
```

Run `make help` to see all 32 available demos.

---

## What is Knowledge Stack?

**Knowledge Stack is a permission-aware data layer for AI agents.** You upload your company's documents (policies, contracts, financials, specs), and KS handles:

- **Chunking & embedding** — your docs are parsed, split, and vectorized automatically
- **Tenant isolation** — each organization's data is completely separated
- **Per-user permissions** — Alice sees security policies, Bob sees engineering docs, same API
- **Version-aware retrieval** — agents always read the latest approved version
- **Cited responses** — every answer traces back to a specific chunk with a UUID

Your agents talk to KS through an **MCP server** (Model Context Protocol) that exposes 10 read-side tools. Any agent framework works — pydantic-ai, LangGraph, LlamaIndex, raw OpenAI, Anthropic, CrewAI.

```
Your Agent (any framework)
    │
    ▼
knowledgestack-mcp (MCP server, 10 tools)
    │
    ▼
Knowledge Stack API (permission-filtered)
    │
    ▼
Your company's documents (chunked, embedded, version-controlled)
```

---

## How it works

Every demo in this cookbook follows the same pattern:

1. **Connect** — your agent spawns the `knowledgestack-mcp` server over stdio
2. **Discover** — agent calls `list_contents` to see available documents
3. **Read** — agent calls `read` to get document text with inline `[chunk:<uuid>]` markers
4. **Cite** — agent produces structured output where every claim carries a chunk citation
5. **Output** — a file artifact (`.md`, `.docx`, `.xlsx`) that's auditable and shareable

The permission filtering happens at step 2-3: KS only returns documents the API key's user is allowed to see. Your agent code doesn't change per user — KS handles the access control.

---

## 32 industry flagships

Each flagship is a complete, runnable demo with seeded sample data, structured output, and real citations.

### 🏦 Banking & Financial Services

| Demo | Command | What it does |
|---|---|---|
| **Credit memo drafter** | `make demo-credit-memo` | Borrower financials + credit policy → auditable credit memo with risk factors |
| **Loan covenant monitor** | `make demo-covenant-monitor` | Quarterly report + loan agreement → covenant compliance report with breach flags |
| **KYC onboarding review** | `make demo-kyc-review` | Customer application + CDD policy → KYC checklist with risk tier |
| **10-K risk analyzer** | `make demo-earnings-risk` | Real SEC 10-K filing → analyst risk-flag memo (Cloudflare FY2025) |

### ⚖️ Legal

| Demo | Command | What it does |
|---|---|---|
| **Contract obligation extractor** | `make demo-contract-obligations` | MSA → categorized shall/must/will clauses with citations |
| **MSA redline vs playbook** | `make demo-msa-redline` | Inbound contract vs your standard terms → deviation memo |

### 📊 Accounting & Tax

| Demo | Command | What it does |
|---|---|---|
| **ASC 606 rev-rec memo** | `make demo-rev-rec-memo` | Customer contract → 5-step ASC 606 analysis with citations |
| **Audit workpaper drafter** | `make demo-audit-workpaper` | Account name → audit workpaper citing PCAOB standards |
| **Tax position memo** | `make demo-tax-memo` | Tax question → research memo citing IRC + Treasury Regs |

### 🩺 Healthcare

| Demo | Command | What it does |
|---|---|---|
| **Prior auth letter** | `make demo-prior-auth` | Patient scenario → prior-authorization letter citing medical-necessity criteria |
| **Clinical trial eligibility** | `make demo-trial-eligibility` | Patient profile → trial eligibility assessment (real ClinicalTrials.gov data) |

### 🛡️ Insurance

| Demo | Command | What it does |
|---|---|---|
| **Claim adjudication memo** | `make demo-claim-memo` | P&C claim → coverage analysis citing policy wording |
| **Subrogation review** | `make demo-subro-review` | Claim file → subrogation recovery opportunity citing NAIC Model 902 |
| **Policy comparison** | `make demo-policy-compare` | Current vs renewal → side-by-side coverage gap analysis |

### 🏠 Real Estate

| Demo | Command | What it does |
|---|---|---|
| **Lease abstract** | `make demo-lease-abstract` | Commercial lease → one-page abstract (term, rent, covenants) |
| **Zoning compliance check** | `make demo-zoning-check` | Address + proposed use → permitted-use analysis (Austin TX LDC) |

### 💼 Sales & Revenue

| Demo | Command | What it does |
|---|---|---|
| **CSV enrichment** | `make demo-csv` | CSV rows → enriched with KB research per row |
| **Research brief** | `make demo-research` | Topic → cited .docx brief |
| **RFP first draft** | `make demo-rfp-draft` | RFP question → grounded response from past proposals |
| **Sales battlecard** | `make demo-battlecard` | Competitor → differentiators + objection handlers |
| **CAIQ compliance fill** | `make demo-compliance` | Security questionnaire → auto-filled with evidence citations |

### 💊 Pharma · ⚡ Energy · 🏛️ Government

| Demo | Command | What it does |
|---|---|---|
| **Adverse event narrative** | `make demo-ae-narrative` | AE data → CIOMS narrative citing drug label |
| **NERC compliance evidence** | `make demo-nerc-evidence` | CIP standard → evidence pack memo |
| **FOIA response drafter** | `make demo-foia-response` | FOIA request → response letter with exemption analysis |

### 👥 HR · ⚙️ Engineering · 🔐 Security

| Demo | Command | What it does |
|---|---|---|
| **Employee handbook Q&A** | `make demo-handbook-qa` | Question → cited answer from company handbook |
| **Job description generator** | `make demo-jd-generator` | Role → JD grounded in leveling guide |
| **Incident runbook lookup** | `make demo-runbook` | Alert → matched runbook steps |
| **API doc generator** | `make demo-api-doc` | Endpoint → developer docs from spec |
| **Release notes** | `make demo-release-notes` | Version → customer-facing notes from specs |
| **Privacy impact assessment** | `make demo-pia` | Feature → PIA memo citing GDPR + template |
| **SOW scope validator** | `make demo-sow-validator` | Proposed SOW → completeness check vs template |
| **Grant compliance checker** | `make demo-grant-compliance` | Sub-awardee activity → compliance memo citing federal regs |

---

## The auth model — identity upstream, permissions in KS

```
              Identity (your IdP)           Permissions (Knowledge Stack)
              ┌──────────────────┐         ┌──────────────────┐
 end-user ────▶ Okta / Azure AD  │──key──▶ │ Knowledge Stack  │──filtered docs──▶ agent
              └──────────────────┘         └──────────────────┘
                     who                      what they can read
```

KS does **not** replace your identity provider. Auth0 / Azure AD / Okta handle login. KS handles **what each user's agent can access** — per-folder, per-document, per-version.

See [`recipes/permission_aware_retrieval/`](recipes/permission_aware_retrieval/) for a live demo: two users, same agent code, different documents returned.

---

## MCP tools (the API surface)

All 32 flagships use these 10 tools from the `knowledgestack-mcp` server:

| Tool | What it does |
|---|---|
| `list_contents` | List children of a folder (or root folders) |
| `find` | Fuzzy-search documents/folders by name |
| `read` | Read a document/section/chunk — returns text with `[chunk:<uuid>]` markers |
| `read_around` | Get surrounding chunks for context |
| `search_knowledge` | Semantic (dense vector) search |
| `search_keyword` | BM25 keyword search |
| `get_info` | Path-part metadata + ancestry breadcrumb |
| `view_chunk_image` | Fetch image content from IMAGE-type chunks |
| `get_organization_info` | Tenant name, language, timezone |
| `get_current_datetime` | Current time in tenant's timezone |

---

## Bring your own data

Every demo works against sample data. To use your own:

1. **Upload documents** to your KS tenant via the web UI or ingestion API
2. **Find your folder's ID** in the KS dashboard (or via `list_contents`)
3. **Run any demo** with your folder:

```bash
CORPUS_FOLDER_ID=your-folder-id make demo-credit-memo
```

The agent code doesn't change — only the data source does.

---

## Using with Claude Desktop / Cursor

Add to your MCP config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

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

Now Claude Desktop / Cursor can search and read your KS tenant directly.

---

## For AI coding agents

This repo is designed to be read by coding agents (Claude Code, Cursor, Copilot). The structure is:

```
flagships/<name>/
  pyproject.toml          # dependencies + CLI entry point
  README.md               # what it does, how to run, sample output
  src/<module>/
    __init__.py
    __main__.py           # CLI: parse args, call agent, write output
    agent.py              # MCP connection + LLM prompt + structured output
    schema.py             # Pydantic output model the LLM must conform to
  sample_inputs/          # default input for the demo
```

To build a new agent: copy any flagship, change the schema + prompt, point at your data. The MCP plumbing stays identical.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Key rules:
- Every output must cite real chunks (`[chunk:<uuid>]`)
- Flagships produce file artifacts, not just stdout
- Use `MODEL` env var so users can swap between gpt-4o / claude / etc.

See [INDUSTRIES.md](INDUSTRIES.md) for 100+ proposed use cases ready for community PRs.

---

## License

MIT — see [LICENSE](LICENSE).
