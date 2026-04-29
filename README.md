<div align="center">

# Knowledge Stack Cookbook

### **Focus on agents. We handle document intelligence.**

**32 production-style flagship agents + 100+ recipes for enterprise RAG — built on [MCP](https://modelcontextprotocol.io/), works with every major agent framework.**

[![GitHub Repo stars](https://img.shields.io/github/stars/knowledgestack/ks-cookbook?style=for-the-badge&logo=github&color=yellow)](https://github.com/knowledgestack/ks-cookbook/stargazers)
[![Discord](https://img.shields.io/badge/Discord-join-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/McHmxUeS)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Flagships](https://img.shields.io/badge/flagships-32-green)](flagships/)
[![Recipes](https://img.shields.io/badge/recipes-100%2B-green)](recipes/)
[![MCP compatible](https://img.shields.io/badge/MCP-compatible-purple)](https://modelcontextprotocol.io/)
[![LangChain](https://img.shields.io/badge/LangChain-supported-brightgreen)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-supported-brightgreen)](https://langchain-ai.github.io/langgraph/)
[![CrewAI](https://img.shields.io/badge/CrewAI-supported-brightgreen)](https://www.crewai.com/)
[![Temporal](https://img.shields.io/badge/Temporal-supported-brightgreen)](https://temporal.io/)

[**Quickstart**](#quickstart) · [**Flagships**](#flagships-by-vertical) · [**Recipes**](recipes/INDEX.md) · [**Wiki**](https://github.com/knowledgestack/ks-cookbook/wiki) · [**Discord**](https://discord.gg/McHmxUeS)

</div>

---

Knowledge Stack is the document intelligence layer behind your agents — ingestion, chunking, permissions, versioning, citations — exposed as a stable **MCP** surface that plugs into [LangChain](https://www.langchain.com/), [LangGraph](https://langchain-ai.github.io/langgraph/), [CrewAI](https://www.crewai.com/), [Temporal](https://temporal.io/), [OpenAI Agents SDK](https://github.com/openai/openai-agents-python), [pydantic-ai](https://ai.pydantic.dev/), [Claude Desktop](https://claude.ai/download), [Cursor](https://cursor.com/), and anything else that speaks [MCP](https://modelcontextprotocol.io/). **Every flagship runs under every framework** — same prompt + schema, framework swaps in.

You focus on agent logic. KS manages the knowledge layer.

→ **New here?** Jump to the [Quickstart](#quickstart) below, or browse the [flagships by vertical](#flagships-by-vertical).

## Index

- 🚀 [Quickstart](#quickstart) — `git clone` → first recipe in ~5 min
- 🧭 [Flagships by vertical](#flagships-by-vertical) — 32 production-style agents, grouped by industry
- 📚 [Recipes index](recipes/INDEX.md) — 100+ ≤100-LOC single-file patterns
- 🔌 Framework integrations: [LangChain](https://www.langchain.com/) · [LangGraph](https://langchain-ai.github.io/langgraph/) · [CrewAI](https://www.crewai.com/) · [Temporal](https://temporal.io/) · [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) · [pydantic-ai](https://ai.pydantic.dev/) · [Claude Desktop](https://claude.ai/download) · [Cursor](https://cursor.com/)
- 🛠 [MCP tools used](#mcp-tools-used) — the 10 read-only tools every flagship calls
- ✍️ [Contributing](CONTRIBUTING.md) · [Industries roadmap](INDUSTRIES.md) · [Wiki](https://github.com/knowledgestack/ks-cookbook/wiki)

## Quickstart

`git clone` → first cited recipe in ~5 minutes.

**Prereqs:** Python `3.11+`, [`uv`](https://docs.astral.sh/uv/), a Knowledge Stack API key (sign in at <https://app.knowledgestack.ai>), and an OpenAI key (`gpt-4o`; `gpt-4o-mini` skips grounding and emits empty citations).

```bash
git clone https://github.com/knowledgestack/ks-cookbook.git
cd ks-cookbook
cp .env.example .env       # then fill in KS_API_KEY + OPENAI_API_KEY
make setup                 # installs every workspace package + validates env
```

Run your first recipe:

```bash
uv run python recipes/icd10_coder/recipe.py \
    --note-file recipes/icd10_coder/sample_inputs/deid_visit_001.txt
```

The agent makes ~10–20 MCP tool calls (`search_knowledge`, `read`, …), then emits a JSON `CodingResult` with real `chunk_id`s pointing into your tenant.

Other quick wins:

```bash
uv run python recipes/clause_extractor/recipe.py --contract "Apple 2024 proxy"
uv run python recipes/contract_renewal_checker/recipe.py --contract "Donna Huang software development"
uv run python recipes/aml_sar_narrative/recipe.py --case-id "structuring-cash-deposits"
make help                  # list every demo target
```

Each recipe folder has its own `README.md` with a captured live output and troubleshooting. To adapt a flagship to your own tenant, override `CORPUS_FOLDER_ID`:

```bash
CORPUS_FOLDER_ID=your-folder-id make demo-credit-memo
```

## Flagships by vertical

32 flagships. Each links to its own README with the expected corpus, a sample input, and a captured sample output — open one to see exactly what it does before running.

Jump to: [Banking](#banking--financial-services) · [Legal](#legal) · [Accounting & tax](#accounting--tax) · [Healthcare](#healthcare) · [Insurance](#insurance) · [Real estate](#real-estate) · [Sales & revenue](#sales--revenue) · [HR](#hr) · [Engineering](#engineering-product--sre) · [Government, pharma, energy](#government-pharma--energy)

### Banking & financial services

- **[Credit memo drafter](flagships/credit_memo_drafter/)** — Cited credit memo from your bank's policy + a borrower's financials.<br/>Tags: `banking` `credit-risk` `underwriting` `commercial-lending`
- **[Loan covenant monitor](flagships/loan_covenant_monitor/)** — Flag covenant breaches from quarterly financials.<br/>Tags: `banking` `covenant-monitoring` `credit-risk`
- **[KYC onboarding review](flagships/kyc_onboarding_review/)** — CDD checklist + risk tier against your KYC policy.<br/>Tags: `banking` `kyc` `aml` `compliance`
- **[Earnings risk analyzer](flagships/earnings_risk_analyzer/)** — Hebbia-style 10-K risk-flag memo with chunk citations.<br/>Tags: `finance` `sec-filings` `10-k` `investment-research`

### Legal

- **[Contract obligation extractor](flagships/contract_obligation_extractor/)** — Every `shall`/`must`/`will` obligation from a contract, categorized + cited.<br/>Tags: `legal` `contracts` `msa` `obligations`
- **[MSA redline vs. playbook](flagships/msa_redline_vs_playbook/)** — Compare an inbound MSA clause-by-clause against your playbook.<br/>Tags: `legal` `contracts` `redline` `negotiations`
- **[Privacy impact assessment](flagships/privacy_impact_assessment/)** — PIA memo citing GDPR Article 35 + company template.<br/>Tags: `legal` `privacy` `gdpr` `security`

### Accounting & tax

- **[Rev-rec memo (ASC 606)](flagships/rev_rec_memo/)** — Five-step revenue-recognition memo grounded in policy.<br/>Tags: `accounting` `asc-606` `revenue-recognition` `memos`
- **[Audit workpaper drafter](flagships/audit_workpaper_drafter/)** — Tie a GL balance to source docs with PCAOB AS 1215 cites.<br/>Tags: `accounting` `audit` `pcaob` `workpapers`
- **[Tax position memo](flagships/tax_position_memo/)** — Tax memo citing IRC sections + Treasury Regs.<br/>Tags: `tax` `irc` `research` `memos`

### Healthcare

- **[Prior-authorization letter](flagships/prior_auth_letter/)** — Cited prior-auth or appeal letter grounded in payer medical policy.<br/>Tags: `healthcare` `prior-auth` `payer` `clinical`
- **[Clinical trial eligibility](flagships/clinical_trial_eligibility/)** — Match a patient against I/E criteria from a real protocol.<br/>Tags: `healthcare` `clinical-trials` `eligibility` `ctms`

### Insurance

- **[Claim adjudication memo](flagships/claim_adjudication_memo/)** — Coverage-analysis memo for a P&C claim.<br/>Tags: `insurance` `claims` `coverage-analysis` `p-and-c`
- **[Subrogation opportunity review](flagships/subrogation_opportunity_review/)** — Recovery potential, citing NAIC Model 902.<br/>Tags: `insurance` `subrogation` `claims`
- **[Insurance policy comparison](flagships/insurance_policy_comparison/)** — Side-by-side analysis with explicit coverage gaps.<br/>Tags: `insurance` `policy-comparison` `coverage`

### Real estate

- **[Lease abstract](flagships/lease_abstract/)** — One-page cited abstract (term, rent, renewals, CAM, exclusives).<br/>Tags: `real-estate` `leases` `commercial`
- **[Zoning compliance check](flagships/zoning_compliance_check/)** — Proposed use vs. local Land Development Code.<br/>Tags: `real-estate` `zoning` `compliance` `municipal`

### Sales & revenue

- **[CSV enrichment](flagships/csv_enrichment/)** — Enrich every CSV row with a short summary from your KB.<br/>Tags: `sales` `data-enrichment` `batch` `operations`
- **[Research brief](flagships/research_brief/)** — Cited `.docx` research brief from your tenant.<br/>Tags: `research` `reports` `analyst`
- **[RFP first draft](flagships/rfp_first_draft/)** — RFP responses grounded in past proposals + capability docs.<br/>Tags: `sales` `rfp` `proposals` `go-to-market`
- **[Sales battlecard](flagships/sales_battlecard/)** — Differentiators, objection handlers, win themes.<br/>Tags: `sales` `competitive` `enablement`
- **[Compliance questionnaire filler](flagships/compliance_questionnaire/)** — Auto-complete CAIQ / SIG from your policy docs.<br/>Tags: `security` `compliance` `caiq` `sig` `questionnaires`

### HR

- **[Employee handbook Q&A](flagships/employee_handbook_qa/)** — Cited answers from the company handbook.<br/>Tags: `hr` `handbook` `q-and-a`
- **[Job description generator](flagships/job_description_generator/)** — JD grounded in leveling + comp bands.<br/>Tags: `hr` `recruiting` `job-descriptions`

### Engineering, product & SRE

- **[Incident runbook lookup](flagships/incident_runbook_lookup/)** — PagerDuty alert → runbook + cited remediation.<br/>Tags: `engineering` `sre` `runbooks` `incident-response`
- **[API doc generator](flagships/api_doc_generator/)** — Endpoint → developer docs from OpenAPI + style guide.<br/>Tags: `engineering` `api` `documentation` `devex`
- **[Release notes generator](flagships/release_notes_generator/)** — Customer-facing notes from specs + migration guide.<br/>Tags: `product` `engineering` `release-notes`
- **[SOW scope validator](flagships/sow_scope_validator/)** — SOW completeness vs. template + methodology.<br/>Tags: `proserv` `sow` `scope-management`

### Government, pharma & energy

- **[Grant compliance checker](flagships/grant_compliance_checker/)** — Sub-awardee activity vs. NOFO + 2 CFR 200.<br/>Tags: `government` `grants` `compliance` `cfr`
- **[FOIA response drafter](flagships/foia_response_drafter/)** — FOIA letter with exemption analysis.<br/>Tags: `government` `foia` `public-records`
- **[Adverse event narrative](flagships/adverse_event_narrative/)** — CIOMS-style AE narrative from drug label + PV SOP.<br/>Tags: `pharma` `pharmacovigilance` `cioms` `safety`
- **[NERC CIP evidence pack](flagships/nerc_compliance_evidence/)** — Compliance evidence memo for a NERC CIP requirement.<br/>Tags: `energy` `nerc-cip` `compliance` `utilities`

## Browse by tag

Tags are first-class metadata declared in each flagship's `pyproject.toml` `[project] keywords`. To find every flagship that uses a given tag, search the repo:

```bash
grep -l '"banking"' flagships/*/pyproject.toml
```

To **add or change tags on a flagship**: edit `keywords = [...]` in its `pyproject.toml`, then run `make tags`.

See [INDUSTRIES.md](INDUSTRIES.md) for the broader roadmap and proposed next flagships.

## Recipes

Short (≤100 LOC) single-file patterns across LangGraph, raw OpenAI, raw Anthropic, and MCP-only — see [`recipes/INDEX.md`](recipes/INDEX.md).

## MCP tools used

Every flagship and recipe in this repo is read-only against your tenant. The 10 MCP tools the agents are allowed to call:

`search_knowledge` · `search_keyword` · `read` · `read_around` · `list_contents` · `find` · `get_info` · `view_chunk_image` · `get_organization_info` · `get_current_datetime`

That's the full contract. Writes are intentionally not exposed.

## Community

- 💬 [**Discord**](https://discord.gg/McHmxUeS) — fastest place to get implementation and architecture help.
- 🗣️ [**GitHub Discussions**](https://github.com/knowledgestack/ks-cookbook/discussions) — long-form questions, propose flagships.
- 🐛 [**Issues**](https://github.com/knowledgestack/ks-cookbook/issues/new/choose) — bugs, [flagship requests](https://github.com/knowledgestack/ks-cookbook/issues/new?template=flagship_request.yml), [recipe requests](https://github.com/knowledgestack/ks-cookbook/issues/new?template=recipe_request.yml), [framework integrations](https://github.com/knowledgestack/ks-cookbook/issues/new?template=framework_integration.yml).
- 🔒 Security: see [SECURITY.md](SECURITY.md). Do **not** open public issues for vulnerabilities.

## Star history

If this repo helps you ship, **[star it](https://github.com/knowledgestack/ks-cookbook)** — it's the single biggest signal we use to decide which flagships, frameworks, and verticals to prioritize next.

<div align="center">
<a href="https://star-history.com/#knowledgestack/ks-cookbook&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=knowledgestack/ks-cookbook&type=Date&theme=dark" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=knowledgestack/ks-cookbook&type=Date" width="700" />
  </picture>
</a>
</div>

## License

MIT. See [LICENSE](LICENSE).
