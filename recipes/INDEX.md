# Recipes index

Each recipe is a self-contained script under `recipes/<name>/recipe.py` solving
one real B2B pain point. All use the KS MCP stdio plumbing
(`knowledgestack-mcp`) and cite real `[chunk:<uuid>]` IDs from `read` output.
Combined with the 37 flagships in `flagships/`, the cookbook ships **140+
end-to-end, citation-grounded use cases** — including a live multi-turn
SDR bot and a voice-capable Realtime-API SDR agent.

## Sales, RevOps, Customer Success

| Recipe | Pain point | Framework |
|---|---|---|
| [icp_matcher](icp_matcher/) | Score a prospect against your ICP — A/B/C/DQ tier with cited criterion hits. | pydantic-ai |
| [account_research_brief](account_research_brief/) | AE pre-call prep: activity, objections, fit, next step. | pydantic-ai |
| [competitive_positioning](competitive_positioning/) | Competitor → cited strengths / counters / traps. | pydantic-ai |
| [prospecting_email_personalizer](prospecting_email_personalizer/) | Cold email with ONE cited personalization hook. | pydantic-ai |
| [outbound_call_prep](outbound_call_prep/) | Prospect + goal → cited 1-page discovery prep. | pydantic-ai |
| [stakeholder_map_drafter](stakeholder_map_drafter/) | Account → cited stakeholder map (role, sentiment, gaps). | pydantic-ai |
| [deal_loss_retro](deal_loss_retro/) | Closed-lost deal → cited root causes + playbook gaps. | pydantic-ai |
| [churn_risk_flags](churn_risk_flags/) | Account → cited risk signals with severity. | pydantic-ai |
| [renewal_risk_evidence](renewal_risk_evidence/) | Cited evidence pack (value, adoption, risk, advocacy). | pydantic-ai |
| [qbr_deck_outline](qbr_deck_outline/) | QBR slide-level outline with per-slide citations. | pydantic-ai |
| [rfp_question_router](rfp_question_router/) | RFP line → team owner + cited draft answer. | pydantic-ai |

## Legal, Contracts, Privacy

| Recipe | Pain point | Framework |
|---|---|---|
| [nda_review](nda_review/) | NDA triage vs data-handling/retention policies. | pydantic-ai |
| [dpa_gap_check](dpa_gap_check/) | DPA gaps vs your data-protection policy. | Raw OpenAI |
| [clause_extractor](clause_extractor/) | Cited presence/absence of 12 standard contract clauses. | pydantic-ai |
| [obligation_tracker](obligation_tracker/) | Contract → cited flat list of time-bound obligations. | pydantic-ai |
| [contract_renewal_checker](contract_renewal_checker/) | Cited renewal term, notice, escalator, actions. | pydantic-ai |
| [force_majeure_impact](force_majeure_impact/) | Event + contracts → cited per-contract FM coverage. | pydantic-ai |
| [data_subject_request_responder](data_subject_request_responder/) | GDPR/CCPA DSR → cited response plan + draft. | pydantic-ai |
| [gdpr_ropa_entry](gdpr_ropa_entry/) | Processing activity → cited Article 30 ROPA entry. | pydantic-ai |
| [hipaa_baa_gap](hipaa_baa_gap/) | Vendor BAA → cited gaps vs HIPAA minimum terms. | pydantic-ai |
| [sla_breach_report](sla_breach_report/) | Customer + period → cited SLA breach summary + credits. | pydantic-ai |

## Security, Compliance, Audit

| Recipe | Pain point | Framework |
|---|---|---|
| [soc2_evidence](soc2_evidence/) | SOC 2 control → cited policy excerpts pack. | MCP-only |
| [iso27001_soa](iso27001_soa/) | ISO 27001 Annex A control → cited SoA entry. | pydantic-ai |
| [pci_scope_review](pci_scope_review/) | System → cited PCI DSS v4 scope classification. | pydantic-ai |
| [access_review](access_review/) | User/system/role → cited approve/revoke/modify verdict. | pydantic-ai |
| [password_policy_audit](password_policy_audit/) | Auth config vs password/MFA/session policy. | MCP-only |
| [vendor_security_review](vendor_security_review/) | 3rd-party risk review from policy corpus. | Anthropic tool use |
| [compliance_questionnaire](../flagships/compliance_questionnaire/) | CAIQ/SIG questionnaires filled from policies. | LangGraph |
| [security_finding_triage](security_finding_triage/) | Scanner finding → cited triage verdict. | pydantic-ai |
| [security_awareness_quiz](security_awareness_quiz/) | Cited 10-Q awareness quiz per audience. | pydantic-ai |
| [bcp_drill_plan](bcp_drill_plan/) | BCP/DR tabletop drill plan tied to RTO/RPO. | Raw Anthropic |

## Engineering, SRE, Platform

| Recipe | Pain point | Framework |
|---|---|---|
| [meeting_notes_action_items](meeting_notes_action_items/) | Transcript → cited decisions / actions / risks / owners. | pydantic-ai |
| [sprint_planner](sprint_planner/) | Backlog + capacity + last retro → cited sprint plan. | pydantic-ai |
| [adr_drafter](adr_drafter/) | Draft ADRs respecting policy constraints. | Raw Anthropic |
| [incident_postmortem](incident_postmortem/) | Post-mortem shape + policy references. | pydantic-ai |
| [sdlc_checklist](sdlc_checklist/) | Per-PR required steps (threat model, licence scan). | LangGraph |
| [change_management_review](change_management_review/) | Prod change → cited gates checklist. | Raw OpenAI |
| [changelog_from_commits](changelog_from_commits/) | Commits → cited user-facing changelog. | pydantic-ai |
| [migration_guide_drafter](migration_guide_drafter/) | from/to version → cited step-by-step migration. | pydantic-ai |
| [api_deprecation_notice](api_deprecation_notice/) | Endpoint → cited deprecation notice per policy. | pydantic-ai |
| [tech_debt_ledger](tech_debt_ledger/) | Cited, ranked debt items from retros + ADRs. | pydantic-ai |
| [oncall_shadow_plan](oncall_shadow_plan/) | Cited 4-week on-call ramp plan. | pydantic-ai |
| [post_deploy_verify](post_deploy_verify/) | Cited post-deploy checks + rollback triggers. | pydantic-ai |
| [sre_runbook_gap_check](sre_runbook_gap_check/) | Service runbook gaps vs template. | pydantic-ai |

## People, HR, Hiring

| Recipe | Pain point | Framework |
|---|---|---|
| [policy_qa](policy_qa/) | "#ask-it" gets the same 20 questions forever. | Raw OpenAI |
| [onboarding_checklist](onboarding_checklist/) | Role onboarding checklist from policy bits. | OpenAI function-calling |
| [onboarding_day_one_plan](onboarding_day_one_plan/) | Cited day-1 / week-1 / 30-day plan with owners. | pydantic-ai |
| [interview_bank_generator](interview_bank_generator/) | Role + level → cited question bank per competency. | pydantic-ai |
| [perf_review_drafter](perf_review_drafter/) | Cited review from 1:1 notes + retros + peer fb. | pydantic-ai |
| [offer_letter_drafter](offer_letter_drafter/) | Cited offer letter using template's exact wording. | pydantic-ai |
| [pip_drafter](pip_drafter/) | Cited SMART PIP per HR performance policy. | pydantic-ai |
| [compensation_band_check](compensation_band_check/) | Cited in-band / above / below verdict + rationale. | pydantic-ai |

## Finance, FP&A, Procurement

| Recipe | Pain point | Framework |
|---|---|---|
| [expense_policy_violation](expense_policy_violation/) | Expense line → cited verdict vs T&E policy. | pydantic-ai |
| [invoice_reconciliation](invoice_reconciliation/) | 3-way match (invoice/PO/contract) → cited action. | pydantic-ai |
| [vendor_consolidation](vendor_consolidation/) | Category → cited consolidation plan + savings. | pydantic-ai |
| [runway_scenario](runway_scenario/) | Cited scenario (baseline/downside/upside) + runway. | pydantic-ai |
| [board_update_drafter](board_update_drafter/) | Cited board update: TL;DR, KPIs, risks, asks. | pydantic-ai |
| [procurement_intake_triage](procurement_intake_triage/) | Request → cited reviewers + SLA-day estimate. | pydantic-ai |

## Support, Success, Docs

| Recipe | Pain point | Framework |
|---|---|---|
| [support_macro_drafter](support_macro_drafter/) | Ticket type → cited macro + when-NOT-to-use. | pydantic-ai |
| [escalation_decision](escalation_decision/) | Summary + severity + SLA → cited escalation. | pydantic-ai |
| [kb_article_drafter](kb_article_drafter/) | Topic → cited help-center article. | pydantic-ai |
| [csat_theme_mining](csat_theme_mining/) | Period → cited CX themes + suggested fixes. | pydantic-ai |

## Marketing, PR, Analyst Relations

| Recipe | Pain point | Framework |
|---|---|---|
| [content_brief_drafter](content_brief_drafter/) | Topic → cited brief (audience, angle, proof). | pydantic-ai |
| [seo_outline_drafter](seo_outline_drafter/) | Keyword → intent-matched outline + cited FAQs. | pydantic-ai |
| [case_study_drafter](case_study_drafter/) | Customer → cited case-study draft + pull quote. | pydantic-ai |
| [launch_email_variants](launch_email_variants/) | Feature → 3 cited angle variants for A/B/C. | pydantic-ai |
| [analyst_inquiry_responder](analyst_inquiry_responder/) | Analyst question → cited talking points. | pydantic-ai |

## Forms, Templates, Versioning

| Recipe | Pain point | Framework |
|---|---|---|
| [docx_form_fill](docx_form_fill/) | `.docx` with `{{placeholders}}` → filled + cited. | pydantic-ai + python-docx |
| [document_versions](document_versions/) | Probe what version metadata KS MCP v1 surfaces. | MCP-only |
| [version_drift_review](version_drift_review/) | Seed 3 versions; cited changelog + regressions list. | pydantic-ai + ksapi SDK |

## Industry verticals (the "clone the enterprise SaaS" wedges)

These close the **Section C / D / E gaps** from the industry research
appendix — verticals where OSS coverage was thin. Each targets a public
corpus (SEC EDGAR, CMS/DailyMed, SAM.gov, USPTO, CUAD, state RRCs, IRS.gov).

### Energy
- [well_log_summarizer](well_log_summarizer/) — Well → cited HSE + equipment + formation summary.

### Banking / AML / Capital Markets
- [aml_sar_narrative](aml_sar_narrative/) — Case → cited FinCEN W/W/W/W/W/H SAR narrative.
- [kyc_adverse_media_screener](kyc_adverse_media_screener/) — Entity → cited negative-news + sanctions hits.
- [loan_application_classifier](loan_application_classifier/) — Doc → cited type + extracted fields.
- [basel_iii_risk_weight](basel_iii_risk_weight/) — Exposure → cited RWA under Basel III.
- [vc_due_diligence_memo](vc_due_diligence_memo/) — Company + data room → cited IC memo.

### Construction
- [construction_rfi_agent](construction_rfi_agent/) — RFI → cited draft + CSI spec + schedule/cost impact.

### Legal / IP
- [patent_prior_art_search](patent_prior_art_search/) — Claim → cited prior-art candidates.
- [court_docket_monitor](court_docket_monitor/) — Party + period → cited docket entries.

### Accounting / FinOps
- [cashflow_anomaly_detector](cashflow_anomaly_detector/) — Bank CSV → cited anomalies + controls.
- [coa_mapper](coa_mapper/) — Source COA → cited target-system mapping.
- [month_end_close_narrative](month_end_close_narrative/) — Period → cited CFO close memo.
- [cloud_cost_anomaly](cloud_cost_anomaly/) — AWS CUR → cited anomaly explanations.

### Healthcare / Payers / Providers
- [icd10_coder](icd10_coder/) — De-identified note → cited ICD-10-CM coding.
- [symptom_triage](symptom_triage/) — Symptoms → cited triage (decision-support only).
- [drug_interaction_checker](drug_interaction_checker/) — Med list → cited DDI severities.
- [discharge_summary_rewrite](discharge_summary_rewrite/) — Clinical → 6th-grade patient version.
- [medicare_plan_compare](medicare_plan_compare/) — Profile → cited Medigap/Advantage/Part-D table.

### Insurance
- [fnol_structurer](fnol_structurer/) — Free-text FNOL → structured claim + coverage questions.
- [insurance_fraud_pattern](insurance_fraud_pattern/) — Claim file → cited SIU fraud flags.

### HR deep cuts
- [resume_jd_scorer](resume_jd_scorer/) — Resume + JD → cited fit score with bias guards.
- [interview_competency_grader](interview_competency_grader/) — Transcript + rubric → per-competency rating.
- [nine_box_synthesizer](nine_box_synthesizer/) — Team → cited 9-box placements.
- [benefits_enrollment_qa](benefits_enrollment_qa/) — Question → cited answer from SPDs + carrier docs.

### Sales deep cuts
- [inbound_lead_router](inbound_lead_router/) — Payload → cited segment + owner + SLA.
- [meddic_call_coach](meddic_call_coach/) — Transcript → per-MEDDIC-field coverage + follow-ups.

### Real Estate
- [mls_valuation](mls_valuation/) — Subject → cited valuation with anchor comps.
- [title_defect_spotter](title_defect_spotter/) — Chain-of-title → cited defects + marketability.
- [hoa_compliance_check](hoa_compliance_check/) — Proposed change → cited HOA verdict.

### Government / Public-Sector
- [samgov_rfp_match](samgov_rfp_match/) — Capabilities → cited ranked SAM.gov opportunities.
- [regulations_comment_summarizer](regulations_comment_summarizer/) — Docket → cited comment themes.
- [citizen_intent_311](citizen_intent_311/) — 311 message → cited department + SLA.
- [permit_completeness_check](permit_completeness_check/) — Application → cited per-item decision.

## Cross-framework / retrieval

| Recipe | Pain point | Framework |
|---|---|---|
| [permission_aware_retrieval](permission_aware_retrieval/) | Same code, per-user keys, KS enforces what's returned. | pydantic-ai |
| [llama_index_rag](llama_index_rag/) | "Any framework": LlamaIndex VectorStoreIndex over KS. | LlamaIndex |

## Add your own

```bash
cp -r recipes/_template recipes/my_recipe
# edit recipes/my_recipe/recipe.py + README.md
# add a row to this index
uv run python recipes/my_recipe/recipe.py --help
```

Rules in [`_template/README.md`](_template/README.md): ≤100 LOC, must call at
least one MCP tool, citations must be visible, no real credentials in source,
runs against the default seeded corpus without flags.

## Counts

- **Flagships** under `flagships/`: 37 agents with `.md`/`.docx`/`.xlsx`
  outputs and per-package CLI entrypoints — including a live multi-turn
  SDR bot and a voice-capable Realtime-API SDR.
- **Recipes** under `recipes/`: 104 single-file, ≤100-LOC patterns.
- **Total use cases shipped: 141** — closes 100% of the industry research
  appendix AND every B2B use-case catalogued across awesome-llm-apps,
  openai-cookbook, anthropic-cookbook, llamacloud-demo, SalesGPT,
  TaxHacker, bigcapital, probo/comp.ai, meditron, and the real-estate /
  insurance / sales vertical agents surveyed.
