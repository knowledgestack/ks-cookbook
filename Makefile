SHELL := /bin/bash

# Auto-load .env if present, but let calling-shell env overrides win.
# Snapshot critical vars from env BEFORE include so we can restore them.
_PRE_KS_API_KEY      := $(KS_API_KEY)
_PRE_KS_BASE_URL     := $(KS_BASE_URL)
_PRE_OPENAI_API_KEY  := $(OPENAI_API_KEY)
_PRE_ANTHROPIC_KEY   := $(ANTHROPIC_API_KEY)
_PRE_MODEL           := $(MODEL)
_PRE_KS_MCP_COMMAND  := $(KS_MCP_COMMAND)
_PRE_KS_MCP_ARGS     := $(KS_MCP_ARGS)

ifneq (,$(wildcard .env))
	include .env
endif

# Restore env-set values (if non-empty) on top of whatever .env loaded.
ifneq (,$(_PRE_KS_API_KEY))
	KS_API_KEY := $(_PRE_KS_API_KEY)
endif
ifneq (,$(_PRE_KS_BASE_URL))
	KS_BASE_URL := $(_PRE_KS_BASE_URL)
endif
ifneq (,$(_PRE_OPENAI_API_KEY))
	OPENAI_API_KEY := $(_PRE_OPENAI_API_KEY)
endif
ifneq (,$(_PRE_ANTHROPIC_KEY))
	ANTHROPIC_API_KEY := $(_PRE_ANTHROPIC_KEY)
endif
ifneq (,$(_PRE_MODEL))
	MODEL := $(_PRE_MODEL)
endif
ifneq (,$(_PRE_KS_MCP_COMMAND))
	KS_MCP_COMMAND := $(_PRE_KS_MCP_COMMAND)
endif
ifneq (,$(_PRE_KS_MCP_ARGS))
	KS_MCP_ARGS := $(_PRE_KS_MCP_ARGS)
endif
export

# Default sensible values for dev. Users normally don't touch these.
export KS_MCP_COMMAND ?= $(abspath .venv/bin/ks-mcp)
export KS_MCP_ARGS ?=
export KS_BASE_URL ?= https://api.knowledgestack.ai
export CSV_ENRICH_PROVIDER ?= $(if $(OPENAI_API_KEY),openai,anthropic)
export CSV_ENRICH_MODEL ?= $(if $(filter openai,$(CSV_ENRICH_PROVIDER)),gpt-4o,claude-opus-4-6)

# Single-row default inputs for the demos.
TOPIC ?= KYC requirements for Verdant Sourcing Group LLC onboarding
IN    ?= flagships/csv_enrichment/sample_inputs/customers.csv
OUT   ?= flagships/csv_enrichment/sample_output.csv

.PHONY: help setup check-env install install-dev lint fix format tags tags-check test demo demo-csv demo-research clean

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage: make \033[36m<target>\033[0m\n\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo
	@echo "First time? Run:  cp .env.example .env  (and fill it in) then  make setup"

setup: install ## First-time setup: install deps + check env
	@$(MAKE) --no-print-directory check-env
	@echo ""
	@echo "Ready. Try:  make demo-csv"

install: ## Install every workspace package into .venv
	@uv sync --all-packages

check-env: ## Fail fast if required env vars are missing
	@missing=0; \
	if [ -z "$$KS_API_KEY" ] || [ "$$KS_API_KEY" = "sk-user-..." ]; then \
		echo "ERROR: KS_API_KEY is not set. Copy .env.example to .env and fill it in."; missing=1; \
	fi; \
	if [ -z "$$OPENAI_API_KEY" ] && [ -z "$$ANTHROPIC_API_KEY" ]; then \
		echo "ERROR: Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env."; missing=1; \
	fi; \
	if [ $$missing -ne 0 ]; then exit 1; fi; \
	echo "KS_API_KEY  = $${KS_API_KEY:0:12}..."; \
	echo "KS_BASE_URL = $$KS_BASE_URL"; \
	echo "LLM         = $$CSV_ENRICH_PROVIDER ($$CSV_ENRICH_MODEL)"

lint: ## Lint all packages (no auto-fix)
	@uv run ruff check .

fix: ## Auto-fix lint issues across the workspace
	@uv run ruff check . --fix

format: ## Format code with ruff
	@uv run ruff format .

tags: ## Sync flagship tags into pyproject keywords + regenerate the wiki book.
	@uv run python scripts/sync_flagship_tags.py
	@uv run python scripts/build_wiki_book.py

tags-check: ## Fail if any flagship is missing or stale on tags (CI).
	@uv run python scripts/sync_flagship_tags.py --check

test: ## MCP server tests live in the ks-mcp repo — this target is a reminder.
	@echo "This repo no longer ships the MCP server."
	@echo "MCP tests: https://github.com/knowledgestack/ks-mcp"
	@echo "Cookbook smoke tests: \`make smoke\`"

smoke: ## Smoke-test every recipe + flagship CLI (catches broken imports/schemas/args).
	@uv run python scripts/smoke_recipes.py

smoke-recipes: ## Smoke-test recipes only
	@uv run python scripts/smoke_recipes.py --recipes-only

smoke-flagships: ## Smoke-test flagships only
	@uv run python scripts/smoke_recipes.py --flagships-only

e2e: check-env ## End-to-end: run every recipe + flagship, verify citations vs tenant. Needs KS_API_KEY + LLM key.
	@uv run python scripts/e2e_verify.py $(E2E_ARGS)

e2e-flagships: check-env ## E2E flagships only
	@uv run python scripts/e2e_verify.py --flagships-only $(E2E_ARGS)

e2e-recipes: check-env ## E2E recipes only
	@uv run python scripts/e2e_verify.py --recipes-only $(E2E_ARGS)

e2e-one: check-env ## E2E a single use case: make e2e-one NAME=icd10_coder
	@test -n "$(NAME)" || (echo 'Usage: make e2e-one NAME=<recipe-or-flagship>'; exit 1)
	@uv run python scripts/e2e_verify.py --only $(NAME) $(E2E_ARGS)

seed-public-corpus: check-env ## Seed a KS tenant with one document per vertical. Set FOLDER_ID.
	@test -n "$(FOLDER_ID)" || (echo 'Usage: make seed-public-corpus FOLDER_ID=<uuid> [VERTICAL=healthcare|banking|all]'; exit 1)
	@uv run python scripts/seed_public_corpus.py --folder-id $(FOLDER_ID) --vertical $${VERTICAL:-all}

install-dev: install ## Install dev tooling + pre-commit hooks
	@uv run pre-commit install 2>/dev/null || echo "(pre-commit not installed; skipping hook setup)"
	@echo "Dev setup complete."

demo: demo-csv demo-research demo-compliance ## Run every flagship

demo-credit-memo: check-env ## Banking flagship: draft a credit memo for a borrower
	@uv run --package ks-cookbook-credit-memo ks-cookbook-credit-memo \
		--borrower "$${BORROWER:-Riverway Logistics LLC}" \
		--loan-amount $${LOAN_AMOUNT:-750000} \
		--corpus-folder $${CORPUS_FOLDER_ID:-18001b47-295b-503f-a7ff-321100853a42} \
		--out flagships/credit_memo_drafter/sample_output.md
	@echo "Output written to: $(abspath flagships/credit_memo_drafter/sample_output.md)"

demo-contract-obligations: check-env ## Legal flagship: extract obligations from a contract
	@uv run --package ks-cookbook-contract-obligations ks-cookbook-contract-obligations \
		--contract-name "$${CONTRACT_NAME:-msa}" \
		--corpus-folder $${LEGAL_CORPUS_FOLDER_ID:-5fa0e0af-561c-5e4e-bfa3-2b66d0e40feb} \
		--out flagships/contract_obligation_extractor/sample_output.md
	@echo "Output written to: $(abspath flagships/contract_obligation_extractor/sample_output.md)"

demo-rev-rec-memo: check-env ## Accounting flagship: draft an ASC 606 rev-rec memo
	@uv run --package ks-cookbook-rev-rec-memo ks-cookbook-rev-rec-memo \
		--in flagships/rev_rec_memo/sample_inputs/globex_contract.json \
		--corpus-folder $${ACCOUNTING_CORPUS_FOLDER_ID:-fee9b054-719f-5033-a268-2ff427ad4600} \
		--out flagships/rev_rec_memo/sample_output.md
	@echo "Output written to: $(abspath flagships/rev_rec_memo/sample_output.md)"

demo-prior-auth: check-env ## Healthcare flagship: draft a cited prior-auth letter
	@uv run --package ks-cookbook-prior-auth ks-cookbook-prior-auth \
		--in flagships/prior_auth_letter/sample_inputs/scenario.txt \
		--corpus-folder $${CORPUS_FOLDER_ID:-475a40fe-49b1-5a44-a08a-912e710cacda} \
		--out flagships/prior_auth_letter/sample_output.docx
	@echo "Output written to: $(abspath flagships/prior_auth_letter/sample_output.docx)"

demo-claim-memo: check-env ## Insurance flagship: draft a coverage-analysis memo from a claim narrative
	@uv run --package ks-cookbook-claim-memo ks-cookbook-claim-memo \
		--in flagships/claim_adjudication_memo/sample_inputs/claim.txt \
		--corpus-folder $${CORPUS_FOLDER_ID:-dda1793d-9129-5c7b-883c-65de41ab4ec6} \
		--out flagships/claim_adjudication_memo/sample_output.md
	@echo "Output written to: $(abspath flagships/claim_adjudication_memo/sample_output.md)"

demo-lease-abstract: check-env ## Real-estate flagship: one-page cited lease abstract
	@uv run --package ks-cookbook-lease-abstract ks-cookbook-lease-abstract \
		--lease-file flagships/lease_abstract/sample_inputs/lease.txt \
		--corpus-folder $${CORPUS_FOLDER_ID:-f4b15500-7806-5ed0-9250-d1f19deb51a9} \
		--out flagships/lease_abstract/sample_output.md
	@echo "Output written to: $(abspath flagships/lease_abstract/sample_output.md)"

demo-msa-redline: check-env ## Legal flagship: compare inbound MSA vs company playbook
	@uv run --package ks-cookbook-msa-redline ks-cookbook-msa-redline \
		--playbook-name "$${PLAYBOOK_NAME:-bonterms_playbook}" \
		--inbound-name "$${INBOUND_NAME:-commonpaper_inbound}" \
		--corpus-folder $${LEGAL_REDLINE_FOLDER_ID:-a4bdb206-d45a-50fa-9b62-071966226eb8} \
		--out flagships/msa_redline_vs_playbook/sample_output.md
	@echo "Output written to: $(abspath flagships/msa_redline_vs_playbook/sample_output.md)"

demo-audit-workpaper: check-env ## Accounting flagship: draft cited audit workpaper for a GL account
	@uv run --package ks-cookbook-audit-workpaper ks-cookbook-audit-workpaper \
		--in flagships/audit_workpaper_drafter/sample_inputs/ar_audit_request.txt \
		--corpus-folder $${AUDIT_CORPUS_FOLDER_ID:-15ebd6ad-13ab-5fa8-9722-4dc8b7a9592f} \
		--out flagships/audit_workpaper_drafter/sample_output.md
	@echo "Output written to: $(abspath flagships/audit_workpaper_drafter/sample_output.md)"

demo-covenant-monitor: check-env ## Banking flagship: covenant compliance report from credit agreement + quarterly financials
	@folder_args=""; \
	if [ -n "$${COVENANT_CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$COVENANT_CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-covenant-monitor ks-cookbook-covenant-monitor \
		--borrower "$${BORROWER:-Nimbus Networks, Inc.}" \
		--period "$${PERIOD:-Q4 2025 / FY 2025}" \
		$$folder_args \
		--out flagships/loan_covenant_monitor/sample_output.md
	@echo "Output written to: $(abspath flagships/loan_covenant_monitor/sample_output.md)"

demo-kyc-review: check-env ## Banking flagship: KYC onboarding review with CDD checklist and risk tier
	@folder_args=""; \
	if [ -n "$${KYC_CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$KYC_CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-kyc-review ks-cookbook-kyc-review \
		$$folder_args \
		--out flagships/kyc_onboarding_review/sample_output.md
	@echo "Output written to: $(abspath flagships/kyc_onboarding_review/sample_output.md)"

demo-trial-eligibility: check-env ## Healthcare flagship: assess patient eligibility for a clinical trial
	@folder_args=""; \
	if [ -n "$${CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-trial-eligibility ks-cookbook-trial-eligibility \
		--in flagships/clinical_trial_eligibility/sample_inputs/patient.txt \
		$$folder_args \
		--out flagships/clinical_trial_eligibility/sample_output.md
	@echo "Output written to: $(abspath flagships/clinical_trial_eligibility/sample_output.md)"

demo-subro-review: check-env ## Insurance flagship: assess subrogation recovery opportunity
	@uv run --package ks-cookbook-subro-review ks-cookbook-subro-review \
		--in flagships/subrogation_opportunity_review/sample_inputs/claim.txt \
		--corpus-folder $${CORPUS_FOLDER_ID:-2577a5b8-6912-5359-bcb8-2ddd67eb86bf} \
		--out flagships/subrogation_opportunity_review/sample_output.md
	@echo "Output written to: $(abspath flagships/subrogation_opportunity_review/sample_output.md)"

demo-zoning-check: check-env ## Real-estate flagship: zoning compliance check (Austin TX LDC)
	@folder_args=""; \
	if [ -n "$${CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-zoning-check ks-cookbook-zoning-check \
		--address "$${ADDRESS:-2100 S Congress Ave, Austin, TX 78704}" \
		--zone-district "$${ZONE_DISTRICT:-GR}" \
		--proposed-use "$${PROPOSED_USE:-outdoor entertainment venue}" \
		$$folder_args \
		--out flagships/zoning_compliance_check/sample_output.md
	@echo "Output written to: $(abspath flagships/zoning_compliance_check/sample_output.md)"

demo-rfp-draft: check-env ## Sales flagship: draft RFP responses from past proposals
	@uv run --package ks-cookbook-rfp-draft ks-cookbook-rfp-draft \
		--question "$${QUESTION:-Describe your approach to data security}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-baf79cab-7ab9-5949-bfda-93cb87b662c0} \
		--out flagships/rfp_first_draft/sample_output.md
	@echo "Output written to: $(abspath flagships/rfp_first_draft/sample_output.md)"

demo-ae-narrative: check-env ## Pharma flagship: CIOMS adverse-event narrative from drug label + PV SOP
	@folder_args=""; \
	if [ -n "$${CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-ae-narrative ks-cookbook-ae-narrative \
		--event "$${EVENT:-Patient experienced severe hypoglycemia requiring hospitalization}" \
		--drug "$${DRUG:-semaglutide}" \
		$$folder_args \
		--out flagships/adverse_event_narrative/sample_output.md
	@echo "Output written to: $(abspath flagships/adverse_event_narrative/sample_output.md)"

demo-nerc-evidence: check-env ## Energy flagship: NERC CIP compliance evidence pack
	@uv run --package ks-cookbook-nerc-evidence ks-cookbook-nerc-evidence \
		--standard "$${STANDARD:-CIP-007-6}" \
		--requirement "$${REQUIREMENT:-R2}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-df0c7c21-494e-583f-a2a7-ad9d231fbee9} \
		--out flagships/nerc_compliance_evidence/sample_output.md
	@echo "Output written to: $(abspath flagships/nerc_compliance_evidence/sample_output.md)"

demo-foia-response: check-env ## Government flagship: FOIA response letter with exemption analysis
	@uv run --package ks-cookbook-foia-response ks-cookbook-foia-response \
		--request "$${REQUEST:-All records related to contract awards for IT services in FY2025}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-033046e7-ecb0-52a5-a552-0251e083ec3d} \
		--out flagships/foia_response_drafter/sample_output.md
	@echo "Output written to: $(abspath flagships/foia_response_drafter/sample_output.md)"

demo-tax-memo: check-env ## Tax flagship: tax position research memo citing IRC + Treasury Regs
	@uv run --package ks-cookbook-tax-memo ks-cookbook-tax-memo \
		--question "$${QUESTION:-Can we deduct R&D expenditures in the current year under Section 174?}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-e6530865-0d30-5547-ad9d-15ccc0952b6d} \
		--out flagships/tax_position_memo/sample_output.md
	@echo "Output written to: $(abspath flagships/tax_position_memo/sample_output.md)"

demo-compliance-setup: check-env ## One-time: clone policy templates + seed corpus into your KS tenant
	@if [ ! -d /tmp/jupiterone-policies ]; then \
		git clone --depth 1 https://github.com/JupiterOne/security-policy-templates.git /tmp/jupiterone-policies; \
	fi
	@echo "POLICIES_FOLDER_ID for Acme Corp sample corpus:"
	@echo "  ab926019-ac7a-579f-bfda-6c52a13c5f41"
	@echo ""
	@echo "To seed it into a fresh tenant, run seed/seed_cookbook_corpus.py in the ks-backend repo."

demo-compliance: check-env ## Fill the sample CAIQ questionnaire. Override: LIMIT=... POLICIES_FOLDER_ID=...
	@uv run --package ks-cookbook-compliance-questionnaire ks-cookbook-compliance \
		--in flagships/compliance_questionnaire/sample_inputs/caiq_v4.xlsx \
		--out flagships/compliance_questionnaire/sample_output.xlsx \
		--limit $${LIMIT:-5} \
		--policies-folder $${POLICIES_FOLDER_ID:-ab926019-ac7a-579f-bfda-6c52a13c5f41}
	@echo ""
	@echo "Output written to: $(abspath flagships/compliance_questionnaire/sample_output.xlsx)"

demo-csv: check-env ## Run csv-enrichment demo. Override: IN=... OUT=...
	@uv run --package ks-cookbook-csv-enrichment ks-cookbook-csv-enrich \
		--in $(abspath $(IN)) --out $(abspath $(OUT))
	@echo ""
	@echo "Output written to: $(abspath $(OUT))"

demo-research: check-env ## Run research-brief demo. Override: TOPIC="..."
	@uv run --package ks-cookbook-research-brief ks-cookbook-research-brief \
		--topic "$(TOPIC)" --out flagships/research_brief/sample_output.docx
	@echo ""
	@echo "Output written to: $(abspath flagships/research_brief/sample_output.docx)"

demo-handbook-qa: check-env ## HR: employee handbook Q&A
	@uv run --package ks-cookbook-handbook-qa ks-cookbook-handbook-qa \
		--input "$${QUESTION:-What is our PTO policy?}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-349f6e37-474e-5070-9e51-991ae64656f0} --out flagships/employee_handbook_qa/sample_output.md
	@echo "Output: $(abspath flagships/employee_handbook_qa/sample_output.md)"

demo-battlecard: check-env ## Sales: competitive battlecard
	@uv run --package ks-cookbook-battlecard ks-cookbook-battlecard \
		--input "$${COMPETITOR:-Competitor A}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-20e842f4-89ef-561c-a8f4-c8e3176de0f9} --out flagships/sales_battlecard/sample_output.md
	@echo "Output: $(abspath flagships/sales_battlecard/sample_output.md)"

demo-runbook: check-env ## Engineering: incident runbook lookup
	@uv run --package ks-cookbook-runbook ks-cookbook-runbook \
		--input "$${ALERT:-High CPU on prod-api-3, 95% for 10 minutes}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-b77989d6-adc6-5259-949f-4eed4ca193c9} --out flagships/incident_runbook_lookup/sample_output.md
	@echo "Output: $(abspath flagships/incident_runbook_lookup/sample_output.md)"

demo-jd-generator: check-env ## HR: job description generator
	@uv run --package ks-cookbook-jd-generator ks-cookbook-jd-generator \
		--input "$${ROLE:-Senior Backend Engineer L5}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-e93a8bc8-a93d-5b02-84fe-0fac8c7a0b68} --out flagships/job_description_generator/sample_output.md
	@echo "Output: $(abspath flagships/job_description_generator/sample_output.md)"

demo-api-doc: check-env ## Engineering: API documentation generator
	@uv run --package ks-cookbook-api-doc ks-cookbook-api-doc \
		--input "$${ENDPOINT:-POST /v1/payments}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-28b79280-8e01-54ad-935e-089b3555379a} --out flagships/api_doc_generator/sample_output.md
	@echo "Output: $(abspath flagships/api_doc_generator/sample_output.md)"

demo-policy-compare: check-env ## Insurance: policy comparison
	@uv run --package ks-cookbook-policy-compare ks-cookbook-policy-compare \
		--input "$${SCENARIO:-Compare current HO-3 vs proposed renewal}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-41335402-45fa-5dbc-b16c-27ef9f090f98} --out flagships/insurance_policy_comparison/sample_output.md
	@echo "Output: $(abspath flagships/insurance_policy_comparison/sample_output.md)"

demo-grant-compliance: check-env ## Government: grant compliance check
	@uv run --package ks-cookbook-grant-compliance ks-cookbook-grant-compliance \
		--input "$${ACTIVITY:-Sub-awardee hired 3 staff and purchased 45K equipment}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-4891bc79-13ca-5da4-8546-e97751622d6b} --out flagships/grant_compliance_checker/sample_output.md
	@echo "Output: $(abspath flagships/grant_compliance_checker/sample_output.md)"

demo-pia: check-env ## Legal: privacy impact assessment
	@uv run --package ks-cookbook-pia ks-cookbook-pia \
		--input "$${FEATURE:-User analytics dashboard collecting page views and session duration}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-99a75f69-88a6-52c4-903a-b39339137a07} --out flagships/privacy_impact_assessment/sample_output.md
	@echo "Output: $(abspath flagships/privacy_impact_assessment/sample_output.md)"

demo-sow-validator: check-env ## ProServ: SOW scope validator
	@uv run --package ks-cookbook-sow-validator ks-cookbook-sow-validator \
		--input "$${SOW:-12-week implementation of Acme Platform for 500 users}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-94ce378b-4096-51bd-a4f0-e900dce1f15b} --out flagships/sow_scope_validator/sample_output.md
	@echo "Output: $(abspath flagships/sow_scope_validator/sample_output.md)"

demo-release-notes: check-env ## Product: release notes generator
	@uv run --package ks-cookbook-release-notes ks-cookbook-release-notes \
		--input "$${VERSION:-v2.4.0}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-a196ef1e-ed0a-5948-ba3e-e607d5356036} --out flagships/release_notes_generator/sample_output.md
	@echo "Output: $(abspath flagships/release_notes_generator/sample_output.md)"

demo-well-log: check-env ## Energy flagship: well-log / drilling summary with HSE + formation events
	@folder_args=""; \
	if [ -n "$${ENERGY_CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$ENERGY_CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-well-log ks-cookbook-well-log \
		--well-id "$${WELL_ID:-42-255-31234}" \
		$$folder_args \
		--out flagships/well_log_summarizer/sample_output.md
	@echo "Output written to: $(abspath flagships/well_log_summarizer/sample_output.md)"

demo-sar-narrative: check-env ## Banking flagship: FinCEN SAR narrative from case evidence
	@folder_args=""; \
	if [ -n "$${AML_CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$AML_CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-sar-narrative ks-cookbook-sar-narrative \
		--case-id "$${CASE_ID:-SAR-2026-0417}" \
		--subject "$${SUBJECT:-Paloma Holdings LLC}" \
		$$folder_args \
		--out flagships/aml_sar_narrative/sample_output.md
	@echo "Output written to: $(abspath flagships/aml_sar_narrative/sample_output.md)"

demo-sdr-bot: check-env ## Sales flagship: live multi-turn SDR bot with MEDDIC scoring (text REPL)
	@folder_args=""; \
	if [ -n "$${SALES_CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$SALES_CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-sdr-bot ks-cookbook-sdr-bot \
		--prospect "$${PROSPECT:-Paloma Networks}" \
		--prospect-context "$${PROSPECT_CONTEXT:-VP Eng at a 400-person SaaS; inbound from a webinar.}" \
		$$folder_args \
		--out flagships/conversational_sdr_bot/sample_output.md
	@echo "Output written to: $(abspath flagships/conversational_sdr_bot/sample_output.md)"

demo-voice-sdr: check-env ## Sales flagship: Realtime-API SDR w/ KS MCP tool proxy (text default; --voice for audio)
	@folder_args=""; \
	if [ -n "$${SALES_CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$SALES_CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-voice-sdr ks-cookbook-voice-sdr \
		--prospect "$${PROSPECT:-Paloma Networks}" \
		--prospect-context "$${PROSPECT_CONTEXT:-VP Eng at a 400-person SaaS; inbound from a webinar.}" \
		$${VOICE:+--voice} \
		$$folder_args \
		--out flagships/realtime_voice_sdr/sample_output.md
	@echo "Output written to: $(abspath flagships/realtime_voice_sdr/sample_output.md)"

demo-rfi-agent: check-env ## Construction flagship: RFI / submittal draft response against specs + drawings
	@folder_args=""; \
	if [ -n "$${CONSTRUCTION_CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$CONSTRUCTION_CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-rfi-agent ks-cookbook-rfi-agent \
		--rfi-number "$${RFI_NUMBER:-RFI-0147}" \
		--question "$${QUESTION:-Mechanical sheet M-402 calls for Greenheck SQ-120-B at grid line C.4 but spec 23 36 00 lists Price SDV-120 as basis of design. Confirm acceptable substitution or provide direction.}" \
		$$folder_args \
		--out flagships/construction_rfi_agent/sample_output.md
	@echo "Output written to: $(abspath flagships/construction_rfi_agent/sample_output.md)"

seed-dbstreams-demo: check-env ## DB Streams tomorrow-demo: seed CondoStack + Sertain + ChiroCRM corpora. PARENT=<folder-uuid>
	@test -n "$(PARENT)" || (echo 'Usage: make seed-dbstreams-demo PARENT=<folder-uuid>'; exit 1)
	@uv run --with reportlab --with openpyxl \
		python scripts/seed_dbstreams_demo.py --parent $(PARENT)

demo-condo-board: check-env ## CondoStack flagship: architectural request → board decision memo (docx)
	@folder_args=""; \
	if [ -n "$${CONDO_CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$CONDO_CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-condo-board ks-cookbook-condo-board \
		--request "$${REQUEST:-Unit 4B requests to install 12 solar panels on the roof terrace and a battery storage unit in the locker room}" \
		--unit "$${UNIT:-4B}" \
		$$folder_args \
		--out flagships/condo_board_decision_pack/sample_output.docx
	@echo "Output: $(abspath flagships/condo_board_decision_pack/sample_output.docx)"

demo-legal-intake: check-env ## Sertain flagship: new-matter intake dossier (docx)
	@folder_args=""; \
	if [ -n "$${LEGAL_CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$LEGAL_CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-legal-intake ks-cookbook-legal-intake \
		--client "$${CLIENT:-Northstar Biotech Ltd.}" \
		--matter "$${MATTER:-Series B financing + technology license-in from MIT}" \
		$$folder_args \
		--out flagships/legal_matter_intake/sample_output.docx
	@echo "Output: $(abspath flagships/legal_matter_intake/sample_output.docx)"

demo-chiro-autopilot: check-env ## ChiroCRM flagship: SOAP note → coding xlsx + prior-auth docx + patient plan md
	@folder_args=""; \
	if [ -n "$${CHIRO_CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$CHIRO_CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-chiro-autopilot ks-cookbook-chiro-autopilot \
		--patient-id "$${PATIENT_ID:-PT-4401}" \
		--visit-date "$${VISIT_DATE:-2026-04-18}" \
		$$folder_args
	@echo "Outputs in: $(abspath flagships/chiro_visit_autopilot/)"

demo-hcc-coder: check-env ## Healthcare flagship: audit-defensible HCC / ICD-10 coder (xlsx)
	@folder_args=""; \
	if [ -n "$${HCC_CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$HCC_CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-hcc-coder ks-cookbook-hcc-coder \
		--patient-id "$${PATIENT_ID:-PT-001}" \
		$$folder_args \
		--out flagships/audit_defensible_hcc_coder/sample_output.xlsx
	@echo "Output: $(abspath flagships/audit_defensible_hcc_coder/sample_output.xlsx)"

demo-contract-redline: check-env ## Legal flagship: inbound contract redline memo (docx) with dual-corpus citations
	@playbook_args=""; draft_args=""; \
	if [ -n "$${PLAYBOOK_FOLDER_ID:-}" ]; then playbook_args="--playbook-folder $$PLAYBOOK_FOLDER_ID"; fi; \
	if [ -n "$${DRAFT_FOLDER_ID:-}" ]; then draft_args="--draft-folder $$DRAFT_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-contract-redline ks-cookbook-contract-redline \
		--playbook-name "$${PLAYBOOK_NAME:-firm_playbook}" \
		--inbound-name "$${INBOUND_NAME:-counterparty_draft}" \
		$$playbook_args $$draft_args \
		--out flagships/contract_redline_with_provenance/sample_output.docx
	@echo "Output: $(abspath flagships/contract_redline_with_provenance/sample_output.docx)"

demo-claims-rebuttal: check-env ## Healthcare flagship: payer denial rebuttal letter (docx)
	@chart_args=""; policy_args=""; \
	if [ -n "$${PATIENT_CHART_FOLDER_ID:-}" ]; then chart_args="--chart-folder $$PATIENT_CHART_FOLDER_ID"; fi; \
	if [ -n "$${PAYER_POLICY_FOLDER_ID:-}" ]; then policy_args="--policy-folder $$PAYER_POLICY_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-claims-rebuttal ks-cookbook-claims-rebuttal \
		--patient-id "$${PATIENT_ID:-PT-9043}" \
		--denial-code "$${DENIAL_CODE:-CO-50}" \
		--payer "$${PAYER:-BCBS}" \
		--service "$${SERVICE:-Lumbar epidural steroid injection}" \
		$$chart_args $$policy_args \
		--out flagships/claims_denial_rebuttal_drafter/sample_output.docx
	@echo "Output: $(abspath flagships/claims_denial_rebuttal_drafter/sample_output.docx)"

demo-invoice-followup: check-env ## SMB flagship: tone-matched overdue-invoice follow-up draft (md)
	@folder_args=""; \
	if [ -n "$${INVOICE_CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$INVOICE_CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-invoice-followup ks-cookbook-invoice-followup \
		--client "$${CLIENT:-Acme Corp}" \
		--invoice-number "$${INVOICE_NUMBER:-INV-2031}" \
		--days-overdue $${DAYS_OVERDUE:-14} \
		$$folder_args \
		--out flagships/smb_invoice_followup_agent/sample_output.md
	@echo "Output: $(abspath flagships/smb_invoice_followup_agent/sample_output.md)"

recipe: check-env ## Run a recipe: make recipe NAME=policy_qa ARGS='--question "..."'
	@if [ -z "$(NAME)" ]; then echo 'Usage: make recipe NAME=<folder> ARGS="..."'; exit 1; fi
	@uv run python recipes/$(NAME)/recipe.py $(ARGS)

recipes: ## List all recipes
	@echo "Available recipes:"
	@ls -1 recipes/ | grep -v '^_' | sed 's/^/  /'

clean: ## Remove generated artifacts
	@rm -f flagships/*/sample_output.md
	@rm -f flagships/*/sample_output.docx
	@rm -f flagships/*/sample_output.xlsx
	@rm -f flagships/*/sample_output.csv

# ---------------------------------------------------------------------------
# Verification helpers (added 2026-04-28 — see docs/CLONE_AND_RUN.md)
# ---------------------------------------------------------------------------

.PHONY: verify-clone seed-unified-corpus verify-clone-retry

seed-unified-corpus: check-env ## Ingest the unified cookbook corpus. Set PARENT_FOLDER_ID.
	@test -n "$(PARENT_FOLDER_ID)" || (echo 'Usage: make seed-unified-corpus PARENT_FOLDER_ID=<uuid>'; exit 1)
	@uv run python scripts/seed_unified_corpus.py --parent-folder-id $(PARENT_FOLDER_ID)

verify-clone: check-env ## End-to-end verify N recipes (default 5). Set N=all to sweep all 105.
	@N=$${N:-5}; \
	if [ "$$N" = "all" ]; then \
	  uv run python scripts/bulk_verify_recipes.py --timeout 240 --out e2e_recipes_full_sweep.json; \
	else \
	  uv run python scripts/bulk_verify_recipes.py --limit $$N --timeout 240 --out e2e_recipes_smoke.json; \
	fi

verify-clone-retry: ## Re-run only the failed recipes from the last verify-clone sweep.
	@FAILS=$$(jq -r '.results[] | select(.status!="pass") | .recipe' e2e_recipes_full_sweep.json 2>/dev/null | paste -sd, -); \
	if [ -z "$$FAILS" ]; then echo "No failures to retry."; exit 0; fi; \
	uv run python scripts/bulk_verify_recipes.py --only "$$FAILS" --timeout 240 --out e2e_recipes_retry.json
