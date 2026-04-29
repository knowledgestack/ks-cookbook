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
[![LangChain](https://img.shields.io/badge/LangChain-supported-brightgreen)](docs/wiki/frameworks/langchain.md)
[![LangGraph](https://img.shields.io/badge/LangGraph-supported-brightgreen)](docs/wiki/frameworks/langgraph.md)
[![CrewAI](https://img.shields.io/badge/CrewAI-supported-brightgreen)](docs/wiki/frameworks/crewai.md)
[![Temporal](https://img.shields.io/badge/Temporal-supported-brightgreen)](docs/wiki/frameworks/temporal.md)

[**Quickstart**](docs/wiki/quickstart.md) · [**Flagships**](#flagships-by-vertical) · [**Frameworks**](docs/wiki/frameworks.md) · [**Wiki**](docs/wiki/README.md) · [**Discord**](https://discord.gg/McHmxUeS)

</div>

---

Knowledge Stack is the document intelligence layer behind your agents — ingestion, chunking, permissions, versioning, citations — exposed as a stable **MCP** surface that plugs into [LangChain](docs/wiki/frameworks/langchain.md), [LangGraph](docs/wiki/frameworks/langgraph.md), [CrewAI](docs/wiki/frameworks/crewai.md), [Temporal](docs/wiki/frameworks/temporal.md), [OpenAI Agents SDK](docs/wiki/frameworks/openai-agents.md), [pydantic-ai](docs/wiki/frameworks/pydantic-ai.md), [Claude Desktop](docs/wiki/frameworks/claude-desktop.md), [Cursor](docs/wiki/frameworks/claude-desktop.md), and anything else that speaks [MCP](https://modelcontextprotocol.io/). **Every flagship runs under every framework** — pick your runtime and the [framework page](docs/wiki/frameworks.md) shows the same flagship ported end-to-end.

You focus on agent logic. KS manages the knowledge layer.

→ **New here?** Read the [Overview](docs/wiki/overview.md) (why this exists, mental model). Then run the [Quickstart](docs/wiki/quickstart.md).

## Index

- 🚀 [Quickstart](docs/wiki/quickstart.md) — `git clone` → first recipe in ~5 min
- 🧠 [Overview & mental model](docs/wiki/overview.md) — what KS manages, pipeline diagram, repo map
- 🔌 [Framework integrations](docs/wiki/frameworks.md) — every flagship runs under every framework. Worked ports:<br/>&nbsp;&nbsp;&nbsp;&nbsp;[pydantic-ai](docs/wiki/frameworks/pydantic-ai.md) · [LangChain](docs/wiki/frameworks/langchain.md) · [LangGraph](docs/wiki/frameworks/langgraph.md) · [CrewAI](docs/wiki/frameworks/crewai.md) · [OpenAI Agents SDK](docs/wiki/frameworks/openai-agents.md) · [Temporal](docs/wiki/frameworks/temporal.md) · [Claude Desktop & Cursor](docs/wiki/frameworks/claude-desktop.md) · [Custom MCP](docs/wiki/frameworks/custom-mcp.md)
- 🛠 [MCP tool reference](docs/wiki/mcp-tools.md) — the 10 read-only tools your agent is allowed to call
- ⚙️ [Configuration](docs/wiki/configuration.md) — env vars, per-demo overrides, base URLs
- 📦 [Seed data](docs/wiki/seed-data.md) — what each flagship expects in your tenant
- ✍️ [Writing a flagship](docs/wiki/writing-a-flagship.md) · [Writing a recipe](docs/wiki/writing-a-recipe.md)
- 🩺 [Troubleshooting](docs/wiki/troubleshooting.md)
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

Click any tag to find every flagship and recipe that uses it (GitHub code search across the repo):

[`accounting`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60accounting%60&type=code) · [`aml`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60aml%60&type=code) · [`api`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60api%60&type=code) · [`asc-606`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60asc-606%60&type=code) · [`audit`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60audit%60&type=code) · [`banking`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60banking%60&type=code) · [`caiq`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60caiq%60&type=code) · [`cfr`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60cfr%60&type=code) · [`cioms`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60cioms%60&type=code) · [`claims`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60claims%60&type=code) · [`clinical`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60clinical%60&type=code) · [`clinical-trials`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60clinical-trials%60&type=code) · [`commercial`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60commercial%60&type=code) · [`compliance`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60compliance%60&type=code) · [`contracts`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60contracts%60&type=code) · [`coverage-analysis`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60coverage-analysis%60&type=code) · [`credit-risk`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60credit-risk%60&type=code) · [`devex`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60devex%60&type=code) · [`energy`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60energy%60&type=code) · [`engineering`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60engineering%60&type=code) · [`finance`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60finance%60&type=code) · [`foia`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60foia%60&type=code) · [`gdpr`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60gdpr%60&type=code) · [`government`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60government%60&type=code) · [`grants`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60grants%60&type=code) · [`healthcare`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60healthcare%60&type=code) · [`hr`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60hr%60&type=code) · [`insurance`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60insurance%60&type=code) · [`kyc`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60kyc%60&type=code) · [`leases`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60leases%60&type=code) · [`legal`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60legal%60&type=code) · [`memos`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60memos%60&type=code) · [`msa`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60msa%60&type=code) · [`nerc-cip`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60nerc-cip%60&type=code) · [`pcaob`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60pcaob%60&type=code) · [`pharma`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60pharma%60&type=code) · [`prior-auth`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60prior-auth%60&type=code) · [`privacy`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60privacy%60&type=code) · [`real-estate`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60real-estate%60&type=code) · [`recruiting`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60recruiting%60&type=code) · [`research`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60research%60&type=code) · [`rfp`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60rfp%60&type=code) · [`runbooks`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60runbooks%60&type=code) · [`sales`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60sales%60&type=code) · [`sec-filings`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60sec-filings%60&type=code) · [`security`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60security%60&type=code) · [`sow`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60sow%60&type=code) · [`sre`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60sre%60&type=code) · [`subrogation`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60subrogation%60&type=code) · [`tax`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60tax%60&type=code) · [`underwriting`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60underwriting%60&type=code) · [`zoning`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%60zoning%60&type=code) · [`10-k`](https://github.com/search?q=repo%3Aknowledgestack%2Fks-cookbook+%6010-k%60&type=code)

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
