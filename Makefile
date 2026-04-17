SHELL := /bin/bash

# Auto-load .env if present. Users copy .env.example → .env and fill it in.
ifneq (,$(wildcard .env))
	include .env
	export
endif

# Default sensible values for dev. Users normally don't touch these.
export KS_MCP_COMMAND ?= $(abspath .venv/bin/ks-mcp)
export KS_MCP_ARGS ?=
export KS_BASE_URL ?= https://api.knowledgestack.ai
export CSV_ENRICH_PROVIDER ?= $(if $(OPENAI_API_KEY),openai,anthropic)
export CSV_ENRICH_MODEL ?= $(if $(filter openai,$(CSV_ENRICH_PROVIDER)),gpt-4o,claude-opus-4-6)

# Single-row default inputs for the demos.
TOPIC ?= KYC requirements for Verdant Sourcing Group LLC onboarding
IN    ?= flagships/csv_enrichment/sample_inputs/customers.csv
OUT   ?= enriched.csv

.PHONY: help setup check-env install lint test demo demo-csv demo-research clean

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

lint: ## Lint all packages
	@uv run ruff check .

test: ## Run unit tests (no live KS needed)
	@uv run --package knowledgestack-mcp --extra dev pytest mcp-python/tests/ -v

demo: demo-csv demo-research demo-compliance ## Run every flagship

demo-credit-memo: check-env ## Banking flagship: draft a credit memo for a borrower
	@uv run --package ks-cookbook-credit-memo ks-cookbook-credit-memo \
		--borrower "$${BORROWER:-Riverway Logistics LLC}" \
		--loan-amount $${LOAN_AMOUNT:-750000} \
		--corpus-folder $${CORPUS_FOLDER_ID:-18001b47-295b-503f-a7ff-321100853a42}
	@echo "Output written to: $(abspath credit-memo.md)"

demo-contract-obligations: check-env ## Legal flagship: extract obligations from a contract
	@uv run --package ks-cookbook-contract-obligations ks-cookbook-contract-obligations \
		--contract-name "$${CONTRACT_NAME:-msa}" \
		--corpus-folder $${LEGAL_CORPUS_FOLDER_ID:-5fa0e0af-561c-5e4e-bfa3-2b66d0e40feb} \
		--out contract-obligations.md
	@echo "Output written to: $(abspath contract-obligations.md)"

demo-rev-rec-memo: check-env ## Accounting flagship: draft an ASC 606 rev-rec memo
	@uv run --package ks-cookbook-rev-rec-memo ks-cookbook-rev-rec-memo \
		--in flagships/rev_rec_memo/sample_inputs/globex_contract.json \
		--corpus-folder $${ACCOUNTING_CORPUS_FOLDER_ID:-fee9b054-719f-5033-a268-2ff427ad4600} \
		--out rev-rec-memo.md
	@echo "Output written to: $(abspath rev-rec-memo.md)"

demo-prior-auth: check-env ## Healthcare flagship: draft a cited prior-auth letter
	@uv run --package ks-cookbook-prior-auth ks-cookbook-prior-auth \
		--in flagships/prior_auth_letter/sample_inputs/scenario.txt \
		--corpus-folder $${CORPUS_FOLDER_ID:-475a40fe-49b1-5a44-a08a-912e710cacda} \
		--out prior-auth-letter.docx
	@echo "Output written to: $(abspath prior-auth-letter.docx)"

demo-claim-memo: check-env ## Insurance flagship: draft a coverage-analysis memo from a claim narrative
	@uv run --package ks-cookbook-claim-memo ks-cookbook-claim-memo \
		--in flagships/claim_adjudication_memo/sample_inputs/claim.txt \
		--corpus-folder $${CORPUS_FOLDER_ID:-dda1793d-9129-5c7b-883c-65de41ab4ec6} \
		--out claim-memo.md
	@echo "Output written to: $(abspath claim-memo.md)"

demo-lease-abstract: check-env ## Real-estate flagship: one-page cited lease abstract
	@uv run --package ks-cookbook-lease-abstract ks-cookbook-lease-abstract \
		--lease-file flagships/lease_abstract/sample_inputs/lease.txt \
		--corpus-folder $${CORPUS_FOLDER_ID:-f4b15500-7806-5ed0-9250-d1f19deb51a9} \
		--out lease-abstract.md
	@echo "Output written to: $(abspath lease-abstract.md)"

demo-msa-redline: check-env ## Legal flagship: compare inbound MSA vs company playbook
	@uv run --package ks-cookbook-msa-redline ks-cookbook-msa-redline \
		--playbook-name "$${PLAYBOOK_NAME:-bonterms_playbook}" \
		--inbound-name "$${INBOUND_NAME:-commonpaper_inbound}" \
		--corpus-folder $${LEGAL_REDLINE_FOLDER_ID:-a4bdb206-d45a-50fa-9b62-071966226eb8} \
		--out msa-redline-memo.md
	@echo "Output written to: $(abspath msa-redline-memo.md)"

demo-audit-workpaper: check-env ## Accounting flagship: draft cited audit workpaper for a GL account
	@uv run --package ks-cookbook-audit-workpaper ks-cookbook-audit-workpaper \
		--in flagships/audit_workpaper_drafter/sample_inputs/ar_audit_request.txt \
		--corpus-folder $${AUDIT_CORPUS_FOLDER_ID:-15ebd6ad-13ab-5fa8-9722-4dc8b7a9592f} \
		--out audit-workpaper.md
	@echo "Output written to: $(abspath audit-workpaper.md)"

demo-covenant-monitor: check-env ## Banking flagship: covenant compliance report from credit agreement + quarterly financials
	@folder_args=""; \
	if [ -n "$${COVENANT_CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$COVENANT_CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-covenant-monitor ks-cookbook-covenant-monitor \
		--borrower "$${BORROWER:-Nimbus Networks, Inc.}" \
		--period "$${PERIOD:-Q4 2025 / FY 2025}" \
		$$folder_args \
		--out covenant-report.md
	@echo "Output written to: $(abspath covenant-report.md)"

demo-kyc-review: check-env ## Banking flagship: KYC onboarding review with CDD checklist and risk tier
	@folder_args=""; \
	if [ -n "$${KYC_CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$KYC_CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-kyc-review ks-cookbook-kyc-review \
		$$folder_args \
		--out kyc-review.md
	@echo "Output written to: $(abspath kyc-review.md)"

demo-trial-eligibility: check-env ## Healthcare flagship: assess patient eligibility for a clinical trial
	@folder_args=""; \
	if [ -n "$${CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-trial-eligibility ks-cookbook-trial-eligibility \
		--in flagships/clinical_trial_eligibility/sample_inputs/patient.txt \
		$$folder_args \
		--out trial-eligibility.md
	@echo "Output written to: $(abspath trial-eligibility.md)"

demo-subro-review: check-env ## Insurance flagship: assess subrogation recovery opportunity
	@uv run --package ks-cookbook-subro-review ks-cookbook-subro-review \
		--in flagships/subrogation_opportunity_review/sample_inputs/claim.txt \
		--corpus-folder $${CORPUS_FOLDER_ID:-2577a5b8-6912-5359-bcb8-2ddd67eb86bf} \
		--out subro-review.md
	@echo "Output written to: $(abspath subro-review.md)"

demo-zoning-check: check-env ## Real-estate flagship: zoning compliance check (Austin TX LDC)
	@folder_args=""; \
	if [ -n "$${CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-zoning-check ks-cookbook-zoning-check \
		--address "$${ADDRESS:-2100 S Congress Ave, Austin, TX 78704}" \
		--zone-district "$${ZONE_DISTRICT:-GR}" \
		--proposed-use "$${PROPOSED_USE:-outdoor entertainment venue}" \
		$$folder_args \
		--out zoning-compliance.md
	@echo "Output written to: $(abspath zoning-compliance.md)"

demo-rfp-draft: check-env ## Sales flagship: draft RFP responses from past proposals
	@uv run --package ks-cookbook-rfp-draft ks-cookbook-rfp-draft \
		--question "$${QUESTION:-Describe your approach to data security}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-baf79cab-7ab9-5949-bfda-93cb87b662c0} \
		--out rfp-draft.md
	@echo "Output written to: $(abspath rfp-draft.md)"

demo-ae-narrative: check-env ## Pharma flagship: CIOMS adverse-event narrative from drug label + PV SOP
	@folder_args=""; \
	if [ -n "$${CORPUS_FOLDER_ID:-}" ]; then folder_args="--corpus-folder $$CORPUS_FOLDER_ID"; fi; \
	uv run --package ks-cookbook-ae-narrative ks-cookbook-ae-narrative \
		--event "$${EVENT:-Patient experienced severe hypoglycemia requiring hospitalization}" \
		--drug "$${DRUG:-semaglutide}" \
		$$folder_args \
		--out ae-narrative.md
	@echo "Output written to: $(abspath ae-narrative.md)"

demo-nerc-evidence: check-env ## Energy flagship: NERC CIP compliance evidence pack
	@uv run --package ks-cookbook-nerc-evidence ks-cookbook-nerc-evidence \
		--standard "$${STANDARD:-CIP-007-6}" \
		--requirement "$${REQUIREMENT:-R2}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-df0c7c21-494e-583f-a2a7-ad9d231fbee9} \
		--out nerc-evidence.md
	@echo "Output written to: $(abspath nerc-evidence.md)"

demo-foia-response: check-env ## Government flagship: FOIA response letter with exemption analysis
	@uv run --package ks-cookbook-foia-response ks-cookbook-foia-response \
		--request "$${REQUEST:-All records related to contract awards for IT services in FY2025}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-033046e7-ecb0-52a5-a552-0251e083ec3d} \
		--out foia-response.md
	@echo "Output written to: $(abspath foia-response.md)"

demo-tax-memo: check-env ## Tax flagship: tax position research memo citing IRC + Treasury Regs
	@uv run --package ks-cookbook-tax-memo ks-cookbook-tax-memo \
		--question "$${QUESTION:-Can we deduct R&D expenditures in the current year under Section 174?}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-e6530865-0d30-5547-ad9d-15ccc0952b6d} \
		--out tax-memo.md
	@echo "Output written to: $(abspath tax-memo.md)"

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
		--out filled.xlsx \
		--limit $${LIMIT:-5} \
		--policies-folder $${POLICIES_FOLDER_ID:-ab926019-ac7a-579f-bfda-6c52a13c5f41}
	@echo ""
	@echo "Output written to: $(abspath filled.xlsx)"

demo-csv: check-env ## Run csv-enrichment demo. Override: IN=... OUT=...
	@uv run --package ks-cookbook-csv-enrichment ks-cookbook-csv-enrich \
		--in $(abspath $(IN)) --out $(abspath $(OUT))
	@echo ""
	@echo "Output written to: $(abspath $(OUT))"

demo-research: check-env ## Run research-brief demo. Override: TOPIC="..."
	@uv run --package ks-cookbook-research-brief ks-cookbook-research-brief \
		--topic "$(TOPIC)" --out brief.docx
	@echo ""
	@echo "Output written to: $(abspath brief.docx)"

demo-handbook-qa: check-env ## HR: employee handbook Q&A
	@uv run --package ks-cookbook-handbook-qa ks-cookbook-handbook-qa \
		--input "$${QUESTION:-What is our PTO policy?}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-349f6e37-474e-5070-9e51-991ae64656f0} --out handbook-qa.md
	@echo "Output: $(abspath handbook-qa.md)"

demo-battlecard: check-env ## Sales: competitive battlecard
	@uv run --package ks-cookbook-battlecard ks-cookbook-battlecard \
		--input "$${COMPETITOR:-Competitor A}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-20e842f4-89ef-561c-a8f4-c8e3176de0f9} --out battlecard.md
	@echo "Output: $(abspath battlecard.md)"

demo-runbook: check-env ## Engineering: incident runbook lookup
	@uv run --package ks-cookbook-runbook ks-cookbook-runbook \
		--input "$${ALERT:-High CPU on prod-api-3, 95% for 10 minutes}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-b77989d6-adc6-5259-949f-4eed4ca193c9} --out runbook.md
	@echo "Output: $(abspath runbook.md)"

demo-jd-generator: check-env ## HR: job description generator
	@uv run --package ks-cookbook-jd-generator ks-cookbook-jd-generator \
		--input "$${ROLE:-Senior Backend Engineer L5}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-e93a8bc8-a93d-5b02-84fe-0fac8c7a0b68} --out jd.md
	@echo "Output: $(abspath jd.md)"

demo-api-doc: check-env ## Engineering: API documentation generator
	@uv run --package ks-cookbook-api-doc ks-cookbook-api-doc \
		--input "$${ENDPOINT:-POST /v1/payments}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-28b79280-8e01-54ad-935e-089b3555379a} --out api-doc.md
	@echo "Output: $(abspath api-doc.md)"

demo-policy-compare: check-env ## Insurance: policy comparison
	@uv run --package ks-cookbook-policy-compare ks-cookbook-policy-compare \
		--input "$${SCENARIO:-Compare current HO-3 vs proposed renewal}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-41335402-45fa-5dbc-b16c-27ef9f090f98} --out policy-compare.md
	@echo "Output: $(abspath policy-compare.md)"

demo-grant-compliance: check-env ## Government: grant compliance check
	@uv run --package ks-cookbook-grant-compliance ks-cookbook-grant-compliance \
		--input "$${ACTIVITY:-Sub-awardee hired 3 staff and purchased 45K equipment}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-4891bc79-13ca-5da4-8546-e97751622d6b} --out grant-compliance.md
	@echo "Output: $(abspath grant-compliance.md)"

demo-pia: check-env ## Legal: privacy impact assessment
	@uv run --package ks-cookbook-pia ks-cookbook-pia \
		--input "$${FEATURE:-User analytics dashboard collecting page views and session duration}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-99a75f69-88a6-52c4-903a-b39339137a07} --out pia.md
	@echo "Output: $(abspath pia.md)"

demo-sow-validator: check-env ## ProServ: SOW scope validator
	@uv run --package ks-cookbook-sow-validator ks-cookbook-sow-validator \
		--input "$${SOW:-12-week implementation of Acme Platform for 500 users}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-94ce378b-4096-51bd-a4f0-e900dce1f15b} --out sow-review.md
	@echo "Output: $(abspath sow-review.md)"

demo-release-notes: check-env ## Product: release notes generator
	@uv run --package ks-cookbook-release-notes ks-cookbook-release-notes \
		--input "$${VERSION:-v2.4.0}" \
		--corpus-folder $${CORPUS_FOLDER_ID:-a196ef1e-ed0a-5948-ba3e-e607d5356036} --out release-notes.md
	@echo "Output: $(abspath release-notes.md)"

recipe: check-env ## Run a recipe: make recipe NAME=policy_qa ARGS='--question "..."'
	@if [ -z "$(NAME)" ]; then echo 'Usage: make recipe NAME=<folder> ARGS="..."'; exit 1; fi
	@uv run python recipes/$(NAME)/recipe.py $(ARGS)

recipes: ## List all recipes
	@echo "Available recipes:"
	@ls -1 recipes/ | grep -v '^_' | sed 's/^/  /'

clean: ## Remove generated artifacts
	@rm -f brief.docx enriched.csv filled.xlsx post-mortem.md prior-auth-letter.docx claim-memo.md lease-abstract.md msa-redline-memo.md audit-workpaper.md covenant-report.md kyc-review.md trial-eligibility.md subro-review.md zoning-compliance.md
