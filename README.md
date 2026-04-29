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
[![LangChain](https://img.shields.io/badge/LangChain-supported-brightgreen)](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/langchain)
[![LangGraph](https://img.shields.io/badge/LangGraph-supported-brightgreen)](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/langgraph)
[![CrewAI](https://img.shields.io/badge/CrewAI-supported-brightgreen)](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/crewai)
[![Temporal](https://img.shields.io/badge/Temporal-supported-brightgreen)](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/temporal)

[**Quickstart**](https://github.com/knowledgestack/ks-cookbook/wiki/quickstart) · [**Flagships**](#flagships-by-vertical) · [**Frameworks**](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks) · [**Wiki**](https://github.com/knowledgestack/ks-cookbook/wiki) · [**Discord**](https://discord.gg/McHmxUeS)

</div>

---

Knowledge Stack is the document intelligence layer behind your agents — ingestion, chunking, permissions, versioning, citations — exposed as a stable **MCP** surface that plugs into [LangChain](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/langchain), [LangGraph](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/langgraph), [CrewAI](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/crewai), [Temporal](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/temporal), [OpenAI Agents SDK](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/openai-agents), [pydantic-ai](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/pydantic-ai), [Claude Desktop](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/claude-desktop), [Cursor](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/claude-desktop), and anything else that speaks [MCP](https://modelcontextprotocol.io/). **Every flagship runs under every framework** — pick your runtime and the [framework page](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks) shows the same flagship ported end-to-end.

You focus on agent logic. KS manages the knowledge layer.

→ **New here?** Read the [Overview](https://github.com/knowledgestack/ks-cookbook/wiki/overview) (why this exists, mental model). Then run the [Quickstart](https://github.com/knowledgestack/ks-cookbook/wiki/quickstart).

## Index

- 🚀 [Quickstart](https://github.com/knowledgestack/ks-cookbook/wiki/quickstart) — `git clone` → first recipe in ~5 min
- 📖 [Cookbook book](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships) — every flagship + recipe README assembled into one navigable book ([flagships](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships) · [recipes](https://github.com/knowledgestack/ks-cookbook/wiki/book/recipes))
- 🧠 [Overview & mental model](https://github.com/knowledgestack/ks-cookbook/wiki/overview) — what KS manages, pipeline diagram, repo map
- 🔌 [Framework integrations](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks) — every flagship runs under every framework. Worked ports:<br/>&nbsp;&nbsp;&nbsp;&nbsp;[pydantic-ai](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/pydantic-ai) · [LangChain](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/langchain) · [LangGraph](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/langgraph) · [CrewAI](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/crewai) · [OpenAI Agents SDK](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/openai-agents) · [Temporal](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/temporal) · [Claude Desktop & Cursor](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/claude-desktop) · [Custom MCP](https://github.com/knowledgestack/ks-cookbook/wiki/frameworks/custom-mcp)
- 🛠 [MCP tool reference](https://github.com/knowledgestack/ks-cookbook/wiki/mcp-tools) — the 10 read-only tools your agent is allowed to call
- ⚙️ [Configuration](https://github.com/knowledgestack/ks-cookbook/wiki/configuration) — env vars, per-demo overrides, base URLs
- 📦 [Seed data](https://github.com/knowledgestack/ks-cookbook/wiki/seed-data) — what each flagship expects in your tenant
- ✍️ [Writing a flagship](https://github.com/knowledgestack/ks-cookbook/wiki/writing-a-flagship) · [Writing a recipe](https://github.com/knowledgestack/ks-cookbook/wiki/writing-a-recipe)
- 🩺 [Troubleshooting](https://github.com/knowledgestack/ks-cookbook/wiki/troubleshooting)
- 🤝 [Contributing](CONTRIBUTING.md) · [Industries roadmap](INDUSTRIES.md)

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

Tags are first-class metadata declared in each flagship's `pyproject.toml` `[project] keywords`. The full tag index — every flagship grouped by tag, with anchor links into the wiki book — lives at **[`https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag`](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag)**.

Quick jumps:

[`banking`](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag#banking) · [`legal`](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag#legal) · [`accounting`](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag#accounting) · [`tax`](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag#tax) · [`healthcare`](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag#healthcare) · [`insurance`](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag#insurance) · [`real-estate`](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag#real-estate) · [`sales`](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag#sales) · [`hr`](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag#hr) · [`engineering`](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag#engineering) · [`compliance`](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag#compliance) · [`security`](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag#security) · [`government`](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag#government) · [`pharma`](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag#pharma) · [`energy`](https://github.com/knowledgestack/ks-cookbook/wiki/book/flagships-by-tag#energy)

To **add or change tags on a flagship**: edit `keywords = [...]` in its `pyproject.toml`, then run `make tags`. See [Writing a flagship → Tagging](https://github.com/knowledgestack/ks-cookbook/wiki/writing-a-flagship#tagging).

See [INDUSTRIES.md](INDUSTRIES.md) for the broader roadmap and proposed next flagships.

## Recipes

Short (≤100 LOC) single-file patterns across LangGraph, raw OpenAI, raw Anthropic, and MCP-only — see [`recipes/INDEX.md`](recipes/INDEX.md).

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
