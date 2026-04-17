# Knowledge Stack Cookbook

> **Focus on agents. We handle document intelligence.**
>
> A developer acceleration layer for enterprise RAG + agent pipelines.

Knowledge Stack is the document intelligence layer behind your agents — ingestion, chunking, permissions, versioning, and citation tracking — exposed through a stable **MCP** surface that plugs into [LangChain](https://www.langchain.com/), [LangGraph](https://langchain-ai.github.io/langgraph/), [CrewAI](https://www.crewai.com/), [Temporal](https://temporal.io/), [OpenAI Agents SDK](https://github.com/openai/openai-agents-python), [pydantic-ai](https://ai.pydantic.dev/), [Claude Desktop](https://claude.ai/download), [Cursor](https://cursor.com/), and anything else that speaks [Model Context Protocol](https://modelcontextprotocol.io/).

This repo is **32 production-style flagship agents + lightweight recipes** showing how to build enterprise RAG pipelines in minutes instead of weeks. Verticals covered: banking, finance, legal, accounting, tax, healthcare, insurance, real estate, sales, HR, engineering, government, pharma, energy.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Flagships](https://img.shields.io/badge/flagships-32-green)](https://github.com/knowledgestack/ks-cookbook/tree/main/flagships)
[![MCP compatible](https://img.shields.io/badge/MCP-compatible-purple)](https://modelcontextprotocol.io/)
[![LangChain](https://img.shields.io/badge/LangChain-supported-brightgreen)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-supported-brightgreen)](https://langchain-ai.github.io/langgraph/)
[![CrewAI](https://img.shields.io/badge/CrewAI-supported-brightgreen)](https://www.crewai.com/)
[![Temporal](https://img.shields.io/badge/Temporal-supported-brightgreen)](https://temporal.io/)

⭐ **[Star this repo](https://github.com/knowledgestack/ks-cookbook)** if you're building enterprise AI — it signals which flagships and frameworks to expand next.

## Why this repo exists

If you're already using LangChain, LangGraph, CrewAI, or Temporal, you've noticed the same thing: the orchestration tooling is mature, but **enterprise document infrastructure is still something every team rebuilds from scratch**.

Most AI demos stop at "here is a chat response." Enterprise teams need stricter:

- outputs reviewable by legal, finance, compliance, operations, or engineering
- citations that point back to source material (chunk-level, verifiable)
- permission-aware retrieval — the same agent behaves differently for different users
- version-aware reads so audits reference the document as of a specific date
- patterns that are easy to copy into real internal tooling

Knowledge Stack provides the enterprise document intelligence layer. This cookbook shows how to plug that layer directly into your agent workflows.

## What Knowledge Stack manages for your agent

Instead of building this yourself:

- document ingestion pipelines (PDF, DOCX, HTML, Markdown, …)
- chunk storage and structured navigation
- permission filtering and ACLs
- version-aware retrieval
- citation grounding (chunk-level UUIDs)
- folder-level access control per user
- structured document read surface (folders → documents → sections → chunks)

Knowledge Stack exposes these as APIs and **MCP tools**. So your team focuses on:

- agent workflows
- orchestration logic (LangGraph nodes, CrewAI crews, Temporal activities)
- output schemas
- automation pipelines
- business logic

## Pipeline mental model

```
┌──────────────────────────────────────────────────────────────┐
│  Agent logic      (LangChain / LangGraph / CrewAI / Temporal │
│                    / OpenAI Agents SDK / pydantic-ai)        │
└────────────────────────────┬─────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────┐
│  Knowledge Stack MCP tools  (read, search, list_contents, …) │
└────────────────────────────┬─────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────┐
│  Permission-aware retrieval   +   version-aware reads        │
└────────────────────────────┬─────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────┐
│  Chunk citations  →  schema-enforced output  →  .md/.docx    │
└──────────────────────────────────────────────────────────────┘
```

Knowledge Stack sits between your agent runtime and your document corpus. Your orchestration layer doesn't change.

## Build enterprise RAG faster

Typical enterprise RAG requires building:

| You would normally build | With Knowledge Stack you skip to |
|---|---|
| ingestion pipelines + chunking + metadata | ✅ done — upload and go |
| ACL filtering per user / group / folder | ✅ enforced on every read |
| version pinning + historical retrieval | ✅ version-aware by default |
| citation-grounded output tracking | ✅ every chunk has a UUID |
| schema-enforced agent outputs | ✅ patterns shown in this cookbook |

You start directly at the agent layer.

## Keep your existing agent framework

Knowledge Stack does not replace your agent runtime. Use it with whatever you already run:

- **[LangChain](https://www.langchain.com/)** / **[langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters)** — see [`flagships/csv_enrichment`](flagships/csv_enrichment/) for a LangGraph example.
- **[LangGraph](https://langchain-ai.github.io/langgraph/)** — used by the adverse-event narrative, audit workpaper, and tax memo flagships.
- **[CrewAI](https://www.crewai.com/)** — plug `knowledgestack-mcp` in as a shared tool across a crew.
- **[Temporal](https://temporal.io/)** — call MCP tools from activities for durable, retriable enterprise workflows.
- **[OpenAI Agents SDK](https://github.com/openai/openai-agents-python)** — native MCP support.
- **[pydantic-ai](https://ai.pydantic.dev/)** — used by most flagships in this repo.
- **[Claude Desktop](https://claude.ai/download)** / **[Cursor](https://cursor.com/)** — add KS as an MCP server in config; your assistant gets tenant-scoped retrieval.
- **Custom Python agents** — speak [MCP](https://modelcontextprotocol.io/) directly.

It replaces the hardest part of enterprise RAG: **document infrastructure**.

## What this repo teaches

Each flagship shows how to:

1. connect an agent to Knowledge Stack via MCP
2. retrieve permission-filtered documents
3. enforce schema-constrained output
4. attach chunk-level citations
5. generate a real artifact (`.md` / `.docx` / `.xlsx` / `.csv`)

These are production agent patterns — not chat toys. Recipes (under [`recipes/`](recipes/)) are ≤100 LOC single-file versions of the same ideas across LangGraph, raw OpenAI, raw Anthropic, and MCP-only.

## Who this is for

Teams building internal AI agents on top of large document collections where **permissions**, **citations**, and **structured outputs** matter. If you're shipping agents into regulated verticals — banking, insurance, healthcare, legal, pharma, energy, government — this repo is aimed directly at you.

## Quickstart

### 1. Prerequisites

- Python `3.11+`
- `uv`
- a Knowledge Stack API key
- an OpenAI or Anthropic API key

### 2. Clone and configure

```bash
git clone https://github.com/knowledgestack/ks-cookbook.git
cd ks-cookbook
cp .env.example .env
```

Fill in `.env`:

```env
KS_API_KEY=sk-user-...
KS_BASE_URL=https://api.knowledgestack.ai
OPENAI_API_KEY=sk-proj-...
# or
ANTHROPIC_API_KEY=...
```

### 3. Install everything

```bash
make setup
```

That installs every workspace package into `.venv`, validates env vars, and gets the cookbook ready to run.

### 4. Run a first flagship

```bash
make demo-credit-memo
```

Expected result:

- the flagship runs through the MCP server against the sample tenant corpus
- it writes a file artifact in the repo root
- you get a developer-friendly output such as `credit-memo.md`

Try a few more:

```bash
make demo-contract-obligations
make demo-rev-rec-memo
make demo-prior-auth
make demo-compliance
make demo-earnings-risk
```

To see the full target list:

```bash
make help
```

## Output examples

These are not toy console logs. The flagships write artifacts a team could actually inspect.

Each flagship writes its output into its own package directory as `sample_output.<ext>`:

- `flagships/credit_memo_drafter/sample_output.md` — cited borrower risk memo
- `flagships/contract_obligation_extractor/sample_output.md` — obligations extracted from an MSA
- `flagships/rev_rec_memo/sample_output.md` — ASC 606 position memo
- `flagships/prior_auth_letter/sample_output.docx` — clinical prior-auth submission
- `flagships/compliance_questionnaire/sample_output.xlsx` — auto-completed CAIQ questionnaire
- `flagships/research_brief/sample_output.docx` — research brief built from KB evidence
- `flagships/csv_enrichment/sample_output.csv` — CSV enriched from KB content

Every output lives beside the flagship that produced it.

## Repo map

```text
flagships/<name>/
  README.md              # flagship-specific walkthrough
  pyproject.toml         # package metadata + entrypoint
  src/<module>/
    __main__.py          # CLI entry
    agent.py             # prompt + MCP interaction
    schema.py            # structured output contract
  sample_inputs/         # default demo inputs

recipes/
  INDEX.md               # lightweight patterns and starter recipes

mcp-python/
  README.md              # Python MCP server package details
```

There are currently 32 flagship packages in the workspace and each one is independently runnable.

## How a flagship is structured

A typical flagship follows this flow:

1. Accept a business input such as a borrower name, endpoint, alert, contract, or patient scenario.
2. Connect to `knowledgestack-mcp`.
3. Search, list, and read the relevant folder contents from Knowledge Stack.
4. Ask the model to produce a schema-constrained answer grounded in that source material.
5. Write the output artifact to disk.

The important part is that the retrieval layer and citation discipline are reusable. Once you understand one flagship, the rest are easy to adapt.

## Flagships by vertical

32 flagship demos. Each links to its own README with the expected corpus, a sample input, and a sample output — open one to see exactly what it does before running anything.

### Banking & financial services

- **[Credit memo drafter](flagships/credit_memo_drafter/)** — Draft a cited credit memo from your bank's credit policy plus a borrower's financials.<br/>Tags: `banking` `credit-risk` `underwriting` `commercial-lending`
- **[Loan covenant monitor](flagships/loan_covenant_monitor/)** — Flag covenant breaches or near-breaches from a borrower's quarterly financials.<br/>Tags: `banking` `covenant-monitoring` `credit-risk`
- **[KYC onboarding review](flagships/kyc_onboarding_review/)** — CDD checklist and risk tier for a new customer against the bank's KYC policy.<br/>Tags: `banking` `kyc` `aml` `compliance`
- **[Earnings risk analyzer](flagships/earnings_risk_analyzer/)** — Hebbia-style 10-K risk-flag memo with chunk-level citations.<br/>Tags: `finance` `sec-filings` `10-k` `investment-research`

### Legal

- **[Contract obligation extractor](flagships/contract_obligation_extractor/)** — Every `shall` / `must` / `will` obligation extracted from a contract, categorized and cited.<br/>Tags: `legal` `contracts` `msa` `obligations`
- **[MSA redline vs. playbook](flagships/msa_redline_vs_playbook/)** — Compare an inbound MSA clause-by-clause against your company's standard playbook.<br/>Tags: `legal` `contracts` `redline` `negotiations`
- **[Privacy impact assessment](flagships/privacy_impact_assessment/)** — PIA memo from a feature description, citing GDPR Article 35 and company template.<br/>Tags: `legal` `privacy` `gdpr` `security`

### Accounting & tax

- **[Rev-rec memo (ASC 606)](flagships/rev_rec_memo/)** — Five-step revenue-recognition memo grounded in your company's rev-rec policy.<br/>Tags: `accounting` `asc-606` `revenue-recognition` `memos`
- **[Audit workpaper drafter](flagships/audit_workpaper_drafter/)** — Tie a GL balance to source documents with citations to PCAOB AS 1215.<br/>Tags: `accounting` `audit` `pcaob` `workpapers`
- **[Tax position memo](flagships/tax_position_memo/)** — Tax research memo citing IRC sections and Treasury Regs.<br/>Tags: `tax` `irc` `research` `memos`

### Healthcare

- **[Prior-authorization letter](flagships/prior_auth_letter/)** — Cited prior-auth or appeal letter grounded in the payer's medical policy.<br/>Tags: `healthcare` `prior-auth` `payer` `clinical`
- **[Clinical trial eligibility](flagships/clinical_trial_eligibility/)** — Match a patient against inclusion/exclusion criteria from a real trial protocol.<br/>Tags: `healthcare` `clinical-trials` `eligibility` `ctms`

### Insurance

- **[Claim adjudication memo](flagships/claim_adjudication_memo/)** — Coverage-analysis memo for a P&C claim, grounded in the applicable policy wording.<br/>Tags: `insurance` `claims` `coverage-analysis` `p-and-c`
- **[Subrogation opportunity review](flagships/subrogation_opportunity_review/)** — Assess recovery potential on a claim, citing NAIC Model 902 and internal SOP.<br/>Tags: `insurance` `subrogation` `claims`
- **[Insurance policy comparison](flagships/insurance_policy_comparison/)** — Side-by-side analysis with explicit coverage gaps.<br/>Tags: `insurance` `policy-comparison` `coverage`

### Real estate

- **[Lease abstract](flagships/lease_abstract/)** — One-page cited abstract (tenant, term, rent, renewals, CAM, exclusives).<br/>Tags: `real-estate` `leases` `commercial`
- **[Zoning compliance check](flagships/zoning_compliance_check/)** — Check a proposed use against local Land Development Code.<br/>Tags: `real-estate` `zoning` `compliance` `municipal`

### Sales & revenue

- **[CSV enrichment](flagships/csv_enrichment/)** — Enrich every row of a CSV with a short summary from your knowledge base.<br/>Tags: `sales` `data-enrichment` `batch` `operations`
- **[Research brief](flagships/research_brief/)** — Generate a cited `.docx` research brief from your tenant.<br/>Tags: `research` `reports` `analyst`
- **[RFP first draft](flagships/rfp_first_draft/)** — Draft RFP responses grounded in past proposals and capability docs.<br/>Tags: `sales` `rfp` `proposals` `go-to-market`
- **[Sales battlecard](flagships/sales_battlecard/)** — Battlecard with differentiators, objection handlers, and win themes.<br/>Tags: `sales` `competitive` `enablement`
- **[Compliance questionnaire filler](flagships/compliance_questionnaire/)** — Auto-complete a CAIQ / SIG questionnaire from your policy docs.<br/>Tags: `security` `compliance` `caiq` `sig` `questionnaires`

### HR

- **[Employee handbook Q&A](flagships/employee_handbook_qa/)** — Cited answers from the company handbook.<br/>Tags: `hr` `handbook` `q-and-a`
- **[Job description generator](flagships/job_description_generator/)** — Full JD grounded in leveling criteria and comp bands.<br/>Tags: `hr` `recruiting` `job-descriptions`

### Engineering, product & SRE

- **[Incident runbook lookup](flagships/incident_runbook_lookup/)** — Match a PagerDuty alert to a runbook with cited remediation steps.<br/>Tags: `engineering` `sre` `runbooks` `incident-response`
- **[API doc generator](flagships/api_doc_generator/)** — Endpoint → developer docs grounded in OpenAPI spec + style guide.<br/>Tags: `engineering` `api` `documentation` `devex`
- **[Release notes generator](flagships/release_notes_generator/)** — Customer-facing notes from specs and migration guide.<br/>Tags: `product` `engineering` `release-notes`
- **[SOW scope validator](flagships/sow_scope_validator/)** — Completeness check of a proposed SOW against template + methodology.<br/>Tags: `proserv` `sow` `scope-management`

### Government, pharma & energy

- **[Grant compliance checker](flagships/grant_compliance_checker/)** — Sub-awardee activity checked against NOFO and 2 CFR 200.<br/>Tags: `government` `grants` `compliance` `cfr`
- **[FOIA response drafter](flagships/foia_response_drafter/)** — FOIA response letter with exemption analysis.<br/>Tags: `government` `foia` `public-records`
- **[Adverse event narrative](flagships/adverse_event_narrative/)** — CIOMS-style AE narrative from drug label + PV SOP.<br/>Tags: `pharma` `pharmacovigilance` `cioms` `safety`
- **[NERC CIP evidence pack](flagships/nerc_compliance_evidence/)** — Compliance evidence memo for a NERC CIP requirement.<br/>Tags: `energy` `nerc-cip` `compliance` `utilities`

### Browse by tag

`accounting` · `aml` · `api` · `asc-606` · `audit` · `banking` · `batch` · `caiq` · `cfr` · `cioms` · `claims` · `clinical` · `clinical-trials` · `commercial` · `commercial-lending` · `compliance` · `contracts` · `coverage` · `coverage-analysis` · `credit-risk` · `ctms` · `data-enrichment` · `devex` · `documentation` · `eligibility` · `enablement` · `energy` · `engineering` · `finance` · `foia` · `gdpr` · `government` · `go-to-market` · `grants` · `handbook` · `healthcare` · `hr` · `incident-response` · `insurance` · `investment-research` · `irc` · `job-descriptions` · `kyc` · `leases` · `legal` · `memos` · `msa` · `municipal` · `negotiations` · `nerc-cip` · `obligations` · `operations` · `payer` · `pcaob` · `pharma` · `pharmacovigilance` · `policy-comparison` · `prior-auth` · `privacy` · `product` · `proposals` · `proserv` · `public-records` · `q-and-a` · `questionnaires` · `real-estate` · `recruiting` · `redline` · `release-notes` · `reports` · `research` · `revenue-recognition` · `rfp` · `runbooks` · `safety` · `sales` · `scope-management` · `sec-filings` · `security` · `sig` · `sow` · `sre` · `subrogation` · `tax` · `underwriting` · `utilities` · `workpapers` · `zoning` · `10-k`

See [INDUSTRIES.md](INDUSTRIES.md) for the broader roadmap and proposed next flagships.

## Core commands

```bash
make setup               # install workspace packages and validate env
make help                # list runnable demos
make lint                # ruff across the workspace
make test                # MCP package tests
make demo-credit-memo    # run one flagship
make demo-csv            # run a lightweight batch enrichment demo
make demo-research       # run the research brief demo
```

## Configuration notes

The cookbook auto-loads `.env` from the repo root.

Relevant variables:

- `KS_API_KEY`: required
- `KS_BASE_URL`: defaults to `https://api.knowledgestack.ai`
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: at least one is required
- `CORPUS_FOLDER_ID`: override the default sample corpus for many demos
- demo-specific variables such as `TOPIC`, `QUESTION`, `BORROWER`, `IN`, and `OUT`

Most flagships ship with seeded defaults, so you can run them without hunting down IDs first. When you want to point a demo at your own data, override the folder ID:

```bash
CORPUS_FOLDER_ID=your-folder-id make demo-credit-memo
```

## Bring your own data

To adapt a flagship to your own tenant:

1. Upload your documents to Knowledge Stack.
2. Identify the target folder.
3. Pass that folder ID into a flagship command.
4. Inspect the generated artifact and verify the citations.

The agent code should stay mostly unchanged. The data source changes; the retrieval and schema pattern does not.

## MCP tools used by the flagships

The demos rely on the `knowledgestack-mcp` read-side tool surface, including:

- `list_contents`
- `find`
- `read`
- `read_around`
- `search_knowledge`
- `search_keyword`
- `get_info`
- `view_chunk_image`
- `get_organization_info`
- `get_current_datetime`

That is the contract most builders should care about when adapting these examples.

## For contributors

This repo is set up to be easy to extend:

- copy a flagship and change the prompt and schema
- keep citations mandatory
- make the output a file artifact, not just stdout
- prefer realistic sample corpora and sample inputs

Useful docs:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [INDUSTRIES.md](INDUSTRIES.md)
- [recipes/INDEX.md](recipes/INDEX.md)
- [mcp-python/README.md](mcp-python/README.md)

## Developer docs

Full developer wiki lives under [`docs/wiki/`](docs/wiki/README.md):

- [Connecting to Knowledge Stack](docs/wiki/connecting.md) — API keys, base URLs, wiring the MCP server into your agent framework.
- [MCP tool reference](docs/wiki/mcp-tools.md) — the ten read-only tools your agent is allowed to call.
- [Seed data required](docs/wiki/seed-data.md) — what each flagship expects in your tenant, and how to seed it.
- [Configuration](docs/wiki/configuration.md) — every env var and per-demo override.
- [Writing a flagship](docs/wiki/writing-a-flagship.md) — file layout, prompt rules, schema shape, Makefile wiring.
- [Writing a recipe](docs/wiki/writing-a-recipe.md) — ≤100-LOC single-file pattern, frontmatter, shared session helper.
- [Troubleshooting](docs/wiki/troubleshooting.md) — common setup and runtime errors.

To scaffold a new flagship:

```bash
cp -r flagships/_template flagships/<your-name>
```

## Using the cookbook from Claude Desktop or Cursor

If you want your assistant to talk directly to Knowledge Stack, add the MCP server to your config:

```json
{
  "mcpServers": {
    "knowledgestack": {
      "command": "uvx",
      "args": ["knowledgestack-mcp"],
      "env": {
        "KS_API_KEY": "sk-user-..."
      }
    }
  }
}
```

## Contributing

We're **actively looking for contributions**. Good first PRs:

- **New flagship** for a vertical we haven't covered (proposals in [INDUSTRIES.md](INDUSTRIES.md))
- **New recipe** (≤100 LOC single file) — patterns across LangChain, LangGraph, CrewAI, Temporal, raw OpenAI / Anthropic are all welcome
- **Expand an existing flagship** to a second framework (e.g. port a pydantic-ai flagship to LangGraph)
- **Improve a sample corpus** or assemble a cleaner public-domain dataset
- **Docs fixes** and clearer developer docs in [`docs/wiki/`](docs/wiki/README.md)

Start here: [CONTRIBUTING.md](CONTRIBUTING.md). Scaffold a new flagship or recipe:

```bash
cp -r flagships/_template flagships/<your-name>
# or
cp -r recipes/_template  recipes/<your-name>
```

## Building something with Knowledge Stack? Reach out.

If you're building an internal agent, ingestion pipeline, or enterprise RAG system on top of Knowledge Stack, **we'd love to hear from you** — whether you want to collaborate on a flagship, need help with a production deployment, or have feedback on the MCP surface.

- 🌐 Website: [knowledgestack.ai](https://knowledgestack.ai)
- 💬 Open a [GitHub issue](https://github.com/knowledgestack/ks-cookbook/issues) or [discussion](https://github.com/knowledgestack/ks-cookbook/discussions)
- 📧 Email the team — details on [knowledgestack.ai](https://knowledgestack.ai)
- ⭐ [Star the repo](https://github.com/knowledgestack/ks-cookbook) — it signals which flagships and frameworks to prioritize next

## Community ask

If this repo helped you ship or prototype something, [star the repository](https://github.com/knowledgestack/ks-cookbook). Stars improve discoverability, help us prioritize which examples to deepen, and validate that open-source, enterprise-grade agent patterns are worth maintaining in the open.

## Keywords

_enterprise RAG, AI agents, agent framework, MCP, Model Context Protocol, LangChain, LangGraph, CrewAI, Temporal workflows, OpenAI Agents SDK, pydantic-ai, Claude Desktop, Cursor, permission-aware retrieval, document intelligence, citation grounding, structured output, tool use, knowledge base, vector search, semantic search, BM25, chunk retrieval, version-aware retrieval, tenant isolation, banking AI, legal AI, healthcare AI, insurance AI, accounting AI, compliance automation, KYC, AML, ASC 606, FOIA, NERC CIP, PCAOB, GDPR, prior authorization, CIOMS, clinical trial eligibility, credit memo, covenant monitoring, MSA redline, rev-rec, audit workpaper, tax research, RFP, sales battlecard, SRE runbooks, API documentation, release notes, PIA, SOW, grant compliance._

## Filing issues & PRs

We've made both as low-friction as possible:

- **New flagship idea?** → [Open a flagship request](https://github.com/knowledgestack/ks-cookbook/issues/new?template=flagship_request.yml)
- **Short recipe pattern?** → [Open a recipe request](https://github.com/knowledgestack/ks-cookbook/issues/new?template=recipe_request.yml)
- **Framework integration (LangChain, CrewAI, Temporal, …)?** → [Open a framework integration issue](https://github.com/knowledgestack/ks-cookbook/issues/new?template=framework_integration.yml)
- **Found a bug?** → [File a bug report](https://github.com/knowledgestack/ks-cookbook/issues/new?template=bug_report.yml)
- **Docs wrong or confusing?** → [Open a docs issue](https://github.com/knowledgestack/ks-cookbook/issues/new?template=docs_improvement.yml)
- **Question or "is anyone else doing this?"** → [Start a discussion](https://github.com/knowledgestack/ks-cookbook/discussions)
- **Security vulnerability?** → [Report privately](https://github.com/knowledgestack/ks-cookbook/security/advisories/new) — do not open a public issue. See [SECURITY.md](SECURITY.md).

Pull requests use a [template](.github/pull_request_template.md) that walks you through summary, test plan, and checklist — nothing fancy, just so reviewers can move fast.

## License

MIT. See [LICENSE](LICENSE).
