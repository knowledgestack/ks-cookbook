# Industries Roadmap

**Knowledge Stack is a permission-aware data layer for agents.** You build
agents your way; KS does grounded retrieval, tenant isolation, per-user
permissions, and version-aware visibility. Every enterprise industry needs
this layer.

This file lists the verticals the cookbook is growing into. Status tags:

- 🟢 **shipped** — working end-to-end with seeded corpus in this repo
- 🟡 **scaffolded** — code + corpus exists; verify before depending on it
- 🔵 **proposed** — community-ready; `cp -r flagships/_template flagships/<your-name>` and send a PR
- ⚪ **backlog** — we've researched the use case; someone should build it

**Target: 100+ flagships, 500+ recipes, every major B2B vertical.**

---

## 🏦 Banking & Financial Services

Compliance-heavy, document-heavy, every task is *"write a memo citing this policy."*

| Status | Flagship | One-line pain |
|---|---|---|
| 🟢 | [credit_memo_drafter](flagships/credit_memo_drafter/) | Every commercial loan needs a cited credit memo — policy + financials + industry benchmarks → auditable markdown. **9 real citations on the sample run.** |
| 🔵 | loan_covenant_monitor | Read a borrower's quarterly report, flag covenant breaches vs the loan agreement. |
| 🔵 | kyc_onboarding_review | New customer docs → missing-evidence checklist + risk tier, grounded in the bank's KYC policy. |
| 🔵 | earnings_qa_bot | Internal analyst asks a question → answer grounded in 10-K/10-Q filings with exhibit-page citations. |
| 🔵 | branch_ops_policy_qa | Teller asks "can we wire > $10K without a second signoff?" → cited answer from ops manual. |
| ⚪ | trade_surveillance_narrative | Flag a trade cluster, draft the compliance-ops narrative from the surveillance policy. |
| ⚪ | aml_sar_draft | Write a Suspicious Activity Report first draft from transaction memos + the bank's AML typology library. |
| ⚪ | treasury_reconciliation_memo | Daily cash break → narrative explanation grounded in the GL + SOP. |
| ⚪ | fair_lending_audit_qa | HMDA audit prep: explain each outlier decision with policy citations. |
| ⚪ | vendor_financial_soundness_review | 3rd-party vendor health check from their audited financials + your vendor-risk framework. |

## ⚖️ Legal

| Status | Flagship | Pain |
|---|---|---|
| 🟢 | [contract_obligation_extractor](flagships/contract_obligation_extractor/) | Pull every shall/must/will from a contract, categorize by obligation-holder, cite clauses. **18 obligations extracted from the sample MSA, each cited to a real chunk.** |
| 🔵 | msa_redline_vs_playbook | Mark up a counterparty's MSA against your redline playbook; every change cited to your standard. |
| 🔵 | dpa_gdpr_gap_check | Is this DPA GDPR-compliant? Compare to a standard template, call out missing clauses. |
| 🔵 | nda_auto_review | 10-second sanity check on inbound NDAs vs your standard terms. |
| 🔵 | force_majeure_impact | Given an event type (pandemic, war, supply shock), which clauses in our signed contracts activate? |
| 🔵 | litigation_hold_scope | Matter type → which custodians, systems, and date ranges are in scope, per the legal hold policy. |
| 🔵 | matter_intake_triage | New matter email → triage to practice group + budget category, grounded in the legal ops SOP. |
| ⚪ | trademark_conflict_check | New product-name idea → cited conflict analysis from IP docs + USPTO TESS data. |
| ⚪ | contract_renewal_calendar | Auto-build a 90-day expiry calendar with key terms per contract. |
| ⚪ | privacy_policy_audit | Public-facing policy vs. actual DPA commitments — flag inconsistencies with citations. |
| ⚪ | privilege_log_builder | Review email corpus; privilege-log entries with justification pointing to privilege rules. |

## 📊 Accounting & Finance

| Status | Flagship | Pain |
|---|---|---|
| 🟢 | [rev_rec_memo](flagships/rev_rec_memo/) | 5-step ASC 606 analysis for a customer contract, grounded in the rev-rec policy. **pydantic-ai + 19 chunks seeded; verified end-to-end.** |
| 🔵 | audit_workpaper_drafter | Auditor asks for support on account X → drafts workpaper tying balance to source docs. |
| 🔵 | lease_accounting_classification | Is this lease ASC 842 operating or finance? Cite the lease + the policy. |
| 🔵 | impairment_narrative | Goodwill / long-lived-asset impairment memo from market signals + internal plan. |
| 🔵 | sox_control_walkthrough | Walkthrough narrative for a given control, citing the SOX documentation + sample transactions. |
| 🔵 | deferred_revenue_reconciliation | Tie invoice-level deferred revenue to GL balance, flag anomalies. |
| 🔵 | tax_position_memo | Position paper for an uncertain tax position with authority citations (IRC, Treasury Regs). |
| 🔵 | expense_policy_violation_detector | Scan expense reports, flag violations with exact policy cite. |
| ⚪ | purchase_order_3way_match | PO ↔ receipt ↔ invoice match narrative + exception memo. |
| ⚪ | cost_accounting_allocation_memo | Allocation method memo with the company's cost-accounting standard as source. |

## 🩺 Healthcare

| Status | Flagship | Pain |
|---|---|---|
| 🟢 | [prior_auth_letter](flagships/prior_auth_letter/) | Patient scenario + requested service → draft prior-auth letter citing the medical-necessity criteria. **pydantic-ai + docx output; 21 chunks seeded; verified end-to-end.** |
| 🔵 | appeal_letter_generator | Denied claim → appeal letter drafted against the plan's own policy bulletin. |
| 🔵 | clinical_trial_eligibility | Patient chart → cite each inclusion/exclusion criterion with match or mismatch. |
| 🔵 | icd10_cpt_suggestion | Clinical note → suggested ICD-10 + CPT codes, cited to coding guidelines. |
| 🔵 | utilization_review_memo | Hospital stay review — cite InterQual/MCG criteria per day. |
| 🔵 | hipaa_breach_notification_draft | Incident summary → draft 30-day breach notice + internal memo citing the policy. |
| 🔵 | mds_narrative_note | Skilled-nursing assessment narrative grounded in the MDS manual. |
| ⚪ | formulary_switch_rationale | Drug-switch letter citing the plan formulary + prior-auth criteria. |
| ⚪ | patient_handout_generator | Condition-specific patient education grounded in the provider's approved library. |

## 🛡️ Insurance

| Status | Flagship | Pain |
|---|---|---|
| 🟢 | [claim_adjudication_memo](flagships/claim_adjudication_memo/) | P&C claim scenario → coverage-analysis memo citing policy wording. **LangGraph ReAct; 22 chunks seeded; verified end-to-end.** |
| 🔵 | subrogation_opportunity_review | Claim file + loss run → cited memo on subrogation likelihood. |
| 🔵 | reserve_adjustment_narrative | Propose reserve change citing the claim file + reserving guidelines. |
| 🔵 | underwriting_referral_memo | Submission doesn't meet auto-quote rules → analyst memo citing the UW guide. |
| 🔵 | reinsurance_treaty_trigger_check | Does this loss attach to the treaty? Cite the treaty wording. |
| 🔵 | broker_appetite_match | Broker submission → which of our programs fit, cited to each program's appetite doc. |
| ⚪ | fraud_indicator_memo | Claim characteristics vs the SIU indicator library → referral memo with evidence. |
| ⚪ | catastrophe_claim_batch_triage | Wildfire/hurricane event → triage batch with citations to CAT SOPs. |

## 🏠 Real Estate

| Status | Flagship | Pain |
|---|---|---|
| 🟢 | [lease_abstract](flagships/lease_abstract/) | Commercial lease PDF → 1-page cited abstract (term, rent, options, covenants). **Raw OpenAI function-calling; 33 chunks seeded; verified end-to-end.** |
| 🔵 | zoning_compliance_check | Proposed use at a site → cite the zoning ordinance + variances granted. |
| 🔵 | environmental_phase_1_summary | Phase I report → executive summary with REC findings cited to specific pages. |
| 🔵 | property_tax_appeal_memo | Assessment + comps → appeal memo citing the comparables doc. |
| 🔵 | rent_roll_variance_analysis | Monthly rent roll → narrative explaining delta vs budget with lease citations. |
| 🔵 | cam_reconciliation_memo | CAM pass-through reconciliation letter to tenant with clause citations. |
| ⚪ | title_policy_exception_review | Title commitment exceptions → memo on material/immaterial with citations. |
| ⚪ | appraisal_review_checklist | Appraisal report → checklist compliance vs USPAP + bank policy. |

## 💼 Sales & Revenue Operations

| Status | Flagship | Pain |
|---|---|---|
| 🟢 | [research_brief](flagships/research_brief/) | Topic → cited 5-section research brief from the KB. |
| 🟢 | [csv_enrichment](flagships/csv_enrichment/) | Bulk-enrich CSV rows from the KB. |
| 🔵 | rfp_first_draft | RFP questions → cited draft answers from your product docs + approved battlecards. |
| 🔵 | account_research_brief | Target account → 1-pager with firmographics + your sales context + past activity. |
| 🔵 | deal_loss_retro | Closed-lost deal → root-cause memo from call notes + deal docs. |
| 🔵 | qbr_deck_content_draft | Customer name → QBR talking points grounded in usage docs + signed MSA commitments. |
| 🔵 | icp_match_score | Inbound lead → cited ICP match score referencing your ICP definition + public data. |
| 🔵 | churn_risk_evidence_pack | Usage drop signal → evidence pack citing tickets, QBR notes, invoice history. |
| ⚪ | cold_email_personalizer | Prospect profile → email variants grounded in pre-approved claims library. |
| ⚪ | competitive_battlecard_refresh | Competitor name → refreshed battlecard citing product docs, G2 snippets, recent releases. |

## 👥 People & HR

| Status | Flagship | Pain |
|---|---|---|
| 🔵 | [onboarding_checklist](recipes/onboarding_checklist/) | (recipe) New-hire role → onboarding plan citing HR + security policies. |
| 🔵 | job_description_generator | Role skeleton → full JD grounded in leveling guide + comp band doc. |
| 🔵 | interview_question_bank | Role → 30-question bank tied to leveling competencies. |
| 🔵 | performance_review_draft | Peer feedback + goals → first-draft review referencing leveling criteria. |
| 🔵 | policy_qa_bot | (recipe shipped) "#ask-hr" slack automation grounded in policy library. |
| 🔵 | immigration_case_checklist | Visa type → required documents checklist from your immigration SOP. |
| 🔵 | performance_improvement_plan | Manager observations → PIP drafted against legal-approved template + doc library. |
| ⚪ | compensation_letter_generator | Promotion event → offer letter grounded in comp band + equity policy. |

## ⚙️ Engineering & Product

| Status | Flagship | Pain |
|---|---|---|
| 🔵 | [sdlc_checklist](recipes/sdlc_checklist/) | (recipe) PR → required pre-merge steps per SDLC + data-protection policies. |
| 🔵 | adr_drafter | Decision topic → ADR draft citing prior ADRs + system docs. |
| 🔵 | [incident_postmortem](recipes/incident_postmortem/) | (recipe) Incident → cited post-mortem referencing IR + breach policies. |
| 🔵 | migration_guide_generator | Deprecation notice → migration guide grounded in current API docs + runbooks. |
| 🔵 | release_notes_from_commits | Tag-to-tag commits + specs → customer-facing release notes. |
| 🔵 | runbook_lookup | Oncall alert → relevant runbook section with citations. |
| 🔵 | architecture_review_prep | System design doc → review-committee checklist citing prior reviews. |
| ⚪ | tech_debt_ledger | Codebase scan + backlog → prioritized tech-debt memo with business-impact citations. |
| ⚪ | api_doc_generator | Endpoint spec → developer doc grounded in style guide + auth docs. |
| ⚪ | incident_drill_script | Scenario → tabletop exercise script tied to IR policy. |

## 🏛️ Government & Public Sector

| Status | Flagship | Pain |
|---|---|---|
| 🔵 | foia_response_drafter | FOIA request → response cover letter + redaction log grounded in agency SOP. |
| 🔵 | grant_compliance_memo | Sub-awardee activity → compliance memo citing NOFO + federal regulations. |
| 🔵 | procurement_sole_source_justification | Vendor choice → sole-source memo citing procurement regs. |
| 🔵 | policy_impact_statement | Regulatory change → agency impact analysis with citations to rule text + FR notices. |
| ⚪ | constituent_services_triage | Constituent letter → draft response + cited agency programs. |
| ⚪ | audit_finding_response | OIG finding → corrective action plan citing agency policy. |

## 💊 Pharma & Life Sciences

| Status | Flagship | Pain |
|---|---|---|
| 🔵 | adverse_event_narrative | MedDRA-coded event → narrative for FDA MedWatch / EMA EudraVigilance citing protocol + SOP. |
| 🔵 | protocol_deviation_memo | Site-reported deviation → sponsor assessment + CAPA memo. |
| 🔵 | medical_affairs_rep_response | Unsolicited question from HCP → scientifically-grounded response with citations to label + published studies. |
| 🔵 | submission_dossier_section_draft | Section X of the CTD/eCTD → draft from earlier modules. |
| ⚪ | standard_response_letter | Med-info common question → approved response letter with reference pack. |
| ⚪ | regulatory_change_impact | New FDA guidance → impact analysis across affected products with citations to current labels. |

## ⚡ Energy & Utilities

| Status | Flagship | Pain |
|---|---|---|
| 🔵 | nerc_compliance_evidence_pack | Control ID → evidence pack citing procedures + audit artifacts. |
| 🔵 | outage_communication_template | Outage scenario → customer communication grounded in comms playbook. |
| 🔵 | safety_incident_report | Field incident summary → OSHA 300 + internal report with policy citations. |
| 🔵 | ppa_obligation_extractor | Power-purchase agreement → obligations + delivery schedule + penalty structure. |
| ⚪ | rate_case_filing_section | Filing section → draft grounded in commission precedent + cost-of-service studies. |
| ⚪ | renewables_site_due_diligence | Site data → DD memo citing environmental, title, interconnection reports. |

---

## Lightweight recipes (one-file, ≤100 LOC)

Recipes live in [`recipes/`](recipes/) and are the fastest way to experiment. Browse [`recipes/INDEX.md`](recipes/INDEX.md) for the 6 shipped recipes and ~50 proposed ones across the same verticals.

## 🟡 Seeded-but-unbuilt flagships (first-PR candidates)

Four industry corpora are **already seeded** into the demo tenant by scripts in `ks-backend/seed/`. The flagship PACKAGE (`flagships/<name>/`) is the outstanding work — each is ~200-300 LOC modelled on `credit_memo_drafter` or `contract_obligation_extractor`.

| Flagship | Corpus already seeded | Folder.id for queries |
|---|---|---|
| `rev_rec_memo` | `seed_accounting_corpus.py` — ASC 606 policy, Acme SaaS MSA, judgments memo (3 docs) | `fee9b054-719f-5033-a268-2ff427ad4600` |
| `prior_auth_letter` | `seed_healthcare_corpus.py` — MRI policy, specialty-drug UM, appeal-letter style guide (3 docs) | `475a40fe-49b1-5a44-a08a-912e710cacda` |
| `claim_adjudication_memo` | `seed_insurance_corpus.py` — homeowners policy, CGL policy, claims SOP (3 docs) | `dda1793d-9129-5c7b-883c-65de41ab4ec6` |
| `lease_abstract` | `seed_realestate_corpus.py` — retail lease, office lease, abstract template (3 docs) | `f4b15500-7806-5ed0-9250-d1f19deb51a9` |

Run the corresponding seed script in the ks-backend repo, copy the printed Folder.id, then `cp -r flagships/credit_memo_drafter flagships/<name>` and adapt the prompt + schema. Send a PR.

## Contributing a flagship

```bash
cp -r flagships/_template flagships/<your-name>
# or scaffold from a sibling:
cp -r flagships/credit_memo_drafter flagships/<your-name>
```

Rules: see [`CONTRIBUTING.md`](CONTRIBUTING.md). Every flagship must seed a
realistic (fake-is-fine) corpus, ground its output in real chunks, and cite
every non-trivial claim. No fabricated citations, ever.

## Inspiration — what's working in the open-source agent ecosystem

We track the patterns developers build for reference. See the
[research appendix](docs/industry-research.md) (auto-generated from scans of
popular agent/RAG repos — LangChain cookbook, LlamaIndex examples, OpenAI
Cookbook, Anthropic Cookbook, CrewAI use cases, community Awesome-lists) for
the 50+ recurring patterns that map onto the flagships above.
