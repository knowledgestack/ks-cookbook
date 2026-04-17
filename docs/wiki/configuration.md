# Configuration

The cookbook auto-loads `.env` from the repo root. Nothing else needs to be exported manually.

## Required

| Variable | Purpose |
|---|---|
| `KS_API_KEY` | Your Knowledge Stack API key. Issued from the dashboard; inherits the permissions of the user it belongs to. |
| `OPENAI_API_KEY` **or** `ANTHROPIC_API_KEY` | LLM used by the example agents. Only one is required. |

`make check-env` (a dependency of every demo target) fails fast if these aren't set.

## Optional globals

| Variable | Default | Purpose |
|---|---|---|
| `KS_BASE_URL` | `https://api.knowledgestack.ai` | Override for staging or self-hosted Knowledge Stack. |
| `KS_MCP_COMMAND` | `.venv/bin/ks-mcp` | Binary the agents spawn for the MCP server. Set to `uvx` to use the published release instead of the workspace build. |
| `KS_MCP_ARGS` | _(empty)_ | Extra args passed to the MCP server (e.g. `--http --port 8765`). |
| `CSV_ENRICH_PROVIDER` | `openai` if `OPENAI_API_KEY` set, else `anthropic` | Which LLM provider the CSV-enrichment demo uses. |
| `CSV_ENRICH_MODEL` | `gpt-4o` / `claude-opus-4-6` | Model id for CSV enrichment. |

## Per-demo overrides

Most flagships accept a `CORPUS_FOLDER_ID` override plus a demo-specific business input. Each Makefile target seeds sensible defaults so `make demo-<name>` works with zero flags — override only when you're pointing at your own data.

| Flagship | Business-input vars | Folder-id var |
|---|---|---|
| `demo-credit-memo` | `BORROWER`, `LOAN_AMOUNT` | `CORPUS_FOLDER_ID` |
| `demo-covenant-monitor` | `BORROWER`, `PERIOD` | `COVENANT_CORPUS_FOLDER_ID` |
| `demo-kyc-review` | — | `KYC_CORPUS_FOLDER_ID` |
| `demo-contract-obligations` | `CONTRACT_NAME` | `LEGAL_CORPUS_FOLDER_ID` |
| `demo-msa-redline` | `PLAYBOOK_NAME`, `INBOUND_NAME` | `LEGAL_REDLINE_FOLDER_ID` |
| `demo-rev-rec-memo` | `IN` (JSON contract path) | `ACCOUNTING_CORPUS_FOLDER_ID` |
| `demo-audit-workpaper` | `IN` | `AUDIT_CORPUS_FOLDER_ID` |
| `demo-prior-auth` | `IN` | `CORPUS_FOLDER_ID` |
| `demo-trial-eligibility` | `IN` | `CORPUS_FOLDER_ID` |
| `demo-claim-memo` | `IN` | `CORPUS_FOLDER_ID` |
| `demo-subro-review` | `IN` | `CORPUS_FOLDER_ID` |
| `demo-policy-compare` | `SCENARIO` | `CORPUS_FOLDER_ID` |
| `demo-lease-abstract` | `--lease-file` | `CORPUS_FOLDER_ID` |
| `demo-zoning-check` | `ADDRESS`, `ZONE_DISTRICT`, `PROPOSED_USE` | `CORPUS_FOLDER_ID` |
| `demo-rfp-draft` | `QUESTION` | `CORPUS_FOLDER_ID` |
| `demo-battlecard` | `COMPETITOR` | `CORPUS_FOLDER_ID` |
| `demo-handbook-qa` | `QUESTION` | `CORPUS_FOLDER_ID` |
| `demo-runbook` | `ALERT` | `CORPUS_FOLDER_ID` |
| `demo-jd-generator` | `ROLE` | `CORPUS_FOLDER_ID` |
| `demo-api-doc` | `ENDPOINT` | `CORPUS_FOLDER_ID` |
| `demo-release-notes` | `VERSION` | `CORPUS_FOLDER_ID` |
| `demo-pia` | `FEATURE` | `CORPUS_FOLDER_ID` |
| `demo-sow-validator` | `SOW` | `CORPUS_FOLDER_ID` |
| `demo-grant-compliance` | `ACTIVITY` | `CORPUS_FOLDER_ID` |
| `demo-ae-narrative` | `EVENT`, `DRUG` | `CORPUS_FOLDER_ID` |
| `demo-nerc-evidence` | `STANDARD`, `REQUIREMENT` | `CORPUS_FOLDER_ID` |
| `demo-foia-response` | `REQUEST` | `CORPUS_FOLDER_ID` |
| `demo-tax-memo` | `QUESTION` | `CORPUS_FOLDER_ID` |
| `demo-compliance` | `LIMIT` | `POLICIES_FOLDER_ID` |
| `demo-csv` | `IN`, `OUT` | — |
| `demo-research` | `TOPIC` | — |

The seeded folder IDs in the Makefile point at the public sample tenant so you can run demos before uploading any of your own data.

## Pointing a demo at your own data

```bash
CORPUS_FOLDER_ID=<your-folder-uuid> make demo-credit-memo BORROWER="Acme Co" LOAN_AMOUNT=1000000
```

The agent code doesn't change — only the folder it reads from.
