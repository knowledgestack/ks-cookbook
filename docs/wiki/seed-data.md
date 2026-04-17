# Seed data required per flagship

Every flagship reads from a folder in your Knowledge Stack tenant. If the folder doesn't exist or is empty, retrieval returns nothing and the demo fails in a way that looks like a bug but isn't.

This page tells you **what documents each flagship expects in its folder** so you can set things up before running.

## One-time setup

1. **Sign up** at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. **Issue an API key** from the dashboard and put it in `.env` at the repo root:
   ```env
   KS_API_KEY=sk-user-...
   ```
3. **Create a folder** for each flagship you want to run (one folder per corpus is easiest). Copy its folder ID from the URL or the folder detail pane.
4. **Upload** the documents listed in the table below into the matching folder. Supported types: `.pdf`, `.docx`, `.md`, `.txt`, `.html`, and more — anything the dashboard's upload UI accepts.
5. **Run** the demo with your folder ID:
   ```bash
   CORPUS_FOLDER_ID=<your-folder-id> make demo-<flagship>
   ```

You don't have to recreate documents from scratch — for most flagships, any reasonable public-domain material that matches the corpus description will produce a usable demo output. The point is grounding, not perfect fidelity.

## Matrix

| Flagship | `make` target | Expected corpus (upload to your folder) |
|---|---|---|
| `adverse_event_narrative` | `demo-ae-narrative` | Drug label (SmPC), pharmacovigilance SOP, CIOMS narrative template. |
| `api_doc_generator` | `demo-api-doc` | OpenAPI spec, integration guide, auth model docs. |
| `audit_workpaper_drafter` | `demo-audit-workpaper` | PCAOB AS 1215, company revenue-recognition policy, trial balance, sample invoices. |
| `claim_adjudication_memo` | `demo-claim-memo` | Homeowners policy form, state regulations, adjuster manual. |
| `clinical_trial_eligibility` | `demo-trial-eligibility` | Trial protocol with inclusion/exclusion criteria, clinical guidance, coverage criteria. |
| `compliance_questionnaire` | `demo-compliance` | A set of security policy documents (e.g. the open-source [JupiterOne policy templates](https://github.com/JupiterOne/security-policy-templates)). |
| `contract_obligation_extractor` | `demo-contract-obligations` | Sample MSA, DPA, NDA. |
| `credit_memo_drafter` | `demo-credit-memo` | Bank credit policy, borrower financials (3y), business plan, industry benchmarks. |
| `csv_enrichment` | `demo-csv` | Any folder whose documents you want to enrich CSV rows against. |
| `earnings_risk_analyzer` | _(manual)_ | A 10-K filing (e.g. downloaded from EDGAR), uploaded as PDF or HTML. |
| `employee_handbook_qa` | `demo-handbook-qa` | Employee handbook: PTO, remote work, expenses, travel, code of conduct. |
| `foia_response_drafter` | `demo-foia-response` | FOIA statute + exemption guidance, agency records, redaction playbook. |
| `grant_compliance_checker` | `demo-grant-compliance` | Federal NOFO, 2 CFR 200 Uniform Guidance, sub-awardee reports. |
| `incident_runbook_lookup` | `demo-runbook` | SRE runbooks: DB failover, API 5xx, cert expiry, memory pressure. |
| `insurance_policy_comparison` | `demo-policy-compare` | Current + proposed renewal policy documents and a comparison checklist. |
| `job_description_generator` | `demo-jd-generator` | Leveling guide, role framework, comp band overview. |
| `kyc_onboarding_review` | `demo-kyc-review` | Bank CDD policy, sanctions guidance, sample customer onboarding file. |
| `lease_abstract` | `demo-lease-abstract` | Retail and/or office lease samples. |
| `loan_covenant_monitor` | `demo-covenant-monitor` | Credit agreement, quarterly financial statements, compliance-certificate template. |
| `msa_redline_vs_playbook` | `demo-msa-redline` | Your company's MSA playbook + an inbound MSA to compare against. |
| `nerc_compliance_evidence` | `demo-nerc-evidence` | NERC CIP standard text, internal evidence packets, audit-response templates. |
| `prior_auth_letter` | `demo-prior-auth` | Payer medical policy, clinical guidelines, prior-auth letter template. |
| `privacy_impact_assessment` | `demo-pia` | GDPR Article 35 guidance, a company PIA template, sample data-flow documentation. |
| `release_notes_generator` | `demo-release-notes` | Product changelog, feature specs, API migration guide. |
| `research_brief` | `demo-research` | Any folder with research-grade source material. |
| `rev_rec_memo` | `demo-rev-rec-memo` | ASC 606 policy, sample MSA, historical judgments memo. |
| `rfp_first_draft` | `demo-rfp-draft` | Past RFP responses, security questionnaire answers, capability docs. |
| `sales_battlecard` | `demo-battlecard` | Product overview, competitive analyses. |
| `sow_scope_validator` | `demo-sow-validator` | SOW template, project methodology, rate card. |
| `subrogation_opportunity_review` | `demo-subro-review` | Subrogation playbook, relevant state-statute excerpts, a sample claim file. |
| `tax_position_memo` | `demo-tax-memo` | IRC section text, Treasury Regs, Rev. Ruls, Tax Court opinions. |
| `zoning_compliance_check` | `demo-zoning-check` | Local Land Development Code excerpts, zoning district tables. |

## Tips for assembling a corpus fast

- **Regulated-domain flagships** (banking, healthcare, energy, tax, FOIA, NERC): start with public regulatory text (IRS, SEC, PCAOB, FDA, DOJ, NERC, etc.) — it's all free, citable, and matches what these agents expect.
- **Policy-style flagships** (handbook, PIA, SOW, runbooks): the [JupiterOne security policy templates](https://github.com/JupiterOne/security-policy-templates) cover a surprising amount and are open-source.
- **Deal/contract flagships** (MSA obligations, rev-rec, KYC): Bonterms and Common Paper publish free standard-form contracts that work as sample inputs.
- **One folder per flagship** keeps things clean. You can reuse folders across flagships that share corpora (e.g. several accounting demos can share one folder).

## What happens if you skip this

- Using a folder ID that doesn't exist in your tenant: `404` from the Knowledge Stack API.
- Using an empty folder: demos return empty output or the agent says "no documents found."
- Using a folder that exists but holds the wrong material: the agent will still emit structured output, but citations will be off-topic.

If a demo returns nothing, the corpus is the first thing to check.

## Default folder IDs in the Makefile

The `Makefile` targets ship with seeded default folder UUIDs (visible in each target). Those IDs point at folders in a shared sample tenant. They don't resolve in tenants you create at signup — they're there for internal testing. As an external developer, always pass your own `CORPUS_FOLDER_ID` (or the relevant per-demo variable — see [configuration.md](configuration.md)).
