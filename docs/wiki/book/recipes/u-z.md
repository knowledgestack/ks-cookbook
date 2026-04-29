# Recipes U-Z

_Generated. Do not edit by hand._

[← Back to recipes book](../recipes.md)

## vc_due_diligence_memo

> Source: [`recipes/vc_due_diligence_memo`](../../../recipes/vc_due_diligence_memo)

### Vc Due Diligence Memo

> **VC due-diligence memo — company + data room → cited IC memo.**

#### Table of contents

1. [What this recipe does](#what-this-recipe-does)
2. [How it works](#how-it-works)
3. [Sign in to Knowledge Stack](#sign-in-to-knowledge-stack)
4. [Ingest the unified corpus](#ingest-the-unified-corpus)
5. [Inputs](#inputs)
6. [Output schema](#output-schema)
7. [Run](#run)
8. [Live verified output](#live-verified-output)
9. [Troubleshooting](#troubleshooting)
10. [Files](#files)

#### What this recipe does

Pain point: a VC associate spends a week turning a data room into a
partner-ready investment-committee memo (team / market / product / traction
/ competition / terms / risks). This recipe reads the data room from KS
and emits the structured memo with citations for every fact.

Framework: pydantic-ai. Tools: list_contents, search_knowledge, read.
Output: stdout (JSON).

#### How it works

1. The recipe spawns the `knowledgestack-mcp` stdio server (auth via `KS_API_KEY`).
2. A pydantic-ai `Agent` is built with a strict pydantic output schema and `gpt-4o`/`gpt-4o-mini`.
3. The agent asks Knowledge Stack natural-language questions via `search_knowledge`. **It never passes folder UUIDs** — KS finds the right document by content.
4. For every search hit the agent calls `read(path_part_id=<hit>)` to retrieve the full chunk text. The trailing `[chunk:<uuid>]` marker is the citation.
5. The validated pydantic object is printed as JSON to stdout. Every `chunk_id` is a verbatim UUID from a real chunk in your tenant.

#### Sign in to Knowledge Stack

**Path A — `ingestion: true` (shared cookbook tenant, fastest)**

Sign in at <https://app.knowledgestack.ai>, request a read-only "Cookbook demo" key, then:

```bash
export KS_API_KEY=sk-user-...
export KS_BASE_URL=https://api.knowledgestack.ai
export OPENAI_API_KEY=sk-...
export MODEL=gpt-4o-mini
```

Skip to step 5 (Run).

**Path B — `ingestion: false` (clone repo, ingest into your own tenant)**

```bash
git clone https://github.com/knowledgestack/ks-cookbook
cd ks-cookbook
make install
export KS_API_KEY=sk-user-...   # your own KS key
export KS_BASE_URL=https://api.knowledgestack.ai
export OPENAI_API_KEY=sk-...
export MODEL=gpt-4o-mini
```

#### Ingest the unified corpus

Path B only — one-time. The bundled `seed/` folder has 34 real public-domain documents (CMS ICD-10, NIST 800-53, IRS Pubs, OCC Handbook, KO 10-K, AAPL 2024 proxy, FAR, NERC CIP, FDA Orange Book, BLS XLSX, CDC PPTX, …). Create a parent folder in your tenant via the UI, then:

```bash
make seed-unified-corpus PARENT_FOLDER_ID=<your-folder-uuid>
```

#### Inputs

| Flag | Type | Required | Default | Help |
|---|---|---|---|---|

| `--company` | str | yes | — |  |

| `--round` | str | yes | — | e.g. 'Seed', 'Series A' |

#### Output schema

`DiligenceMemo` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `company` | `str` |

| `round_` | `str` |

| `recommendation` | `str` |

| `tl_dr` | `str` |

| `team` | `list[Finding]` |

| `market` | `list[Finding]` |

| `product` | `list[Finding]` |

| `traction` | `list[Finding]` |

| `competition` | `list[Finding]` |

| `terms_and_structure` | `list[Finding]` |

| `risks` | `list[Risk]` |

#### Run

```bash
uv run python recipes/vc_due_diligence_memo/recipe.py \
    --company FreshFinTech \
    --round "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~105.6s):

```json
{
  "company": "FreshFinTech",
  "round": "demo",
  "recommendation": "diligence_deeper",
  "tl_dr": "FreshFinTech is positioned in the EdTech sector, focusing on maritime and merchant navy training. The team comprises experienced founders;
```

Every `chunk_id` is a verbatim UUID from a `[chunk:<uuid>]` marker; snippets and document names are real chunk content from the ingested corpus.

#### Troubleshooting

| Symptom | Fix |
|---|---|
| `Set KS_API_KEY and OPENAI_API_KEY.` | Export both env vars before running. |
| `Tool 'read' exceeded max retries` | gpt-4o-mini occasionally calls `read(<chunk_id>)` instead of `read(<path_part_id>)`. Re-run; the prompt self-corrects within `retries=4`. Switching to `MODEL=gpt-4o` removes the flake. |
| Empty / non-grounded output | The corpus isn't ingested into your tenant. Run `make seed-unified-corpus PARENT_FOLDER_ID=<uuid>`. |
| `Connection error` from OpenAI | Transient; retry. |
| `request_limit of 50` exceeded | The agent looped too many tools. Re-run; this is rare. |

#### Files

```text
recipes/vc_due_diligence_memo/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## vendor_consolidation

> Source: [`recipes/vendor_consolidation`](../../../recipes/vendor_consolidation)

### Vendor Consolidation

> **Vendor consolidation planning agent using Knowledge Stack MCP.**

#### Table of contents

1. [What this recipe does](#what-this-recipe-does)
2. [How it works](#how-it-works)
3. [Sign in to Knowledge Stack](#sign-in-to-knowledge-stack)
4. [Ingest the unified corpus](#ingest-the-unified-corpus)
5. [Inputs](#inputs)
6. [Output schema](#output-schema)
7. [Run](#run)
8. [Live verified output](#live-verified-output)
9. [Troubleshooting](#troubleshooting)
10. [Files](#files)

#### What this recipe does

Purpose
-------
Generate a procurement vendor consolidation plan for a category
(e.g. observability, CRM, contact-center) using grounded citations
from contracts, renewal notes, and vendor evaluation material.

Example usage
-------------
python consolidate.py   --category observability   --save

#### How it works

1. The recipe spawns the `knowledgestack-mcp` stdio server (auth via `KS_API_KEY`).
2. A pydantic-ai `Agent` is built with a strict pydantic output schema and `gpt-4o`/`gpt-4o-mini`.
3. The agent asks Knowledge Stack natural-language questions via `search_knowledge`. **It never passes folder UUIDs** — KS finds the right document by content.
4. For every search hit the agent calls `read(path_part_id=<hit>)` to retrieve the full chunk text. The trailing `[chunk:<uuid>]` marker is the citation.
5. The validated pydantic object is printed as JSON to stdout. Every `chunk_id` is a verbatim UUID from a real chunk in your tenant.

#### Sign in to Knowledge Stack

**Path A — `ingestion: true` (shared cookbook tenant, fastest)**

Sign in at <https://app.knowledgestack.ai>, request a read-only "Cookbook demo" key, then:

```bash
export KS_API_KEY=sk-user-...
export KS_BASE_URL=https://api.knowledgestack.ai
export OPENAI_API_KEY=sk-...
export MODEL=gpt-4o-mini
```

Skip to step 5 (Run).

**Path B — `ingestion: false` (clone repo, ingest into your own tenant)**

```bash
git clone https://github.com/knowledgestack/ks-cookbook
cd ks-cookbook
make install
export KS_API_KEY=sk-user-...   # your own KS key
export KS_BASE_URL=https://api.knowledgestack.ai
export OPENAI_API_KEY=sk-...
export MODEL=gpt-4o-mini
```

#### Ingest the unified corpus

Path B only — one-time. The bundled `seed/` folder has 34 real public-domain documents (CMS ICD-10, NIST 800-53, IRS Pubs, OCC Handbook, KO 10-K, AAPL 2024 proxy, FAR, NERC CIP, FDA Orange Book, BLS XLSX, CDC PPTX, …). Create a parent folder in your tenant via the UI, then:

```bash
make seed-unified-corpus PARENT_FOLDER_ID=<your-folder-uuid>
```

#### Inputs

| Flag | Type | Required | Default | Help |
|---|---|---|---|---|

| `--category` | str | yes | — | example: observability, CRM, contact-center |

| `--save` | str | no | — | persist output JSON locally |

#### Output schema

`ConsolidationPlan` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `category` | `str` |

| `vendors` | `list[VendorAction]` |

| `overall_savings_estimate` | `str` |

| `risks` | `list[str]` |

#### Run

```bash
uv run python recipes/vendor_consolidation/recipe.py \
    --category entertainment
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~52.9s):

```json
{
  "category": "entertainment",
  "vendors": [
    {
      "vendor": "Nvidia",
      "action": "keep",
      "rationale": "Strategically relevant vendor with effective solutions for managing risks related to foreign currency contracts and
```

Every `chunk_id` is a verbatim UUID from a `[chunk:<uuid>]` marker; snippets and document names are real chunk content from the ingested corpus.

#### Troubleshooting

| Symptom | Fix |
|---|---|
| `Set KS_API_KEY and OPENAI_API_KEY.` | Export both env vars before running. |
| `Tool 'read' exceeded max retries` | gpt-4o-mini occasionally calls `read(<chunk_id>)` instead of `read(<path_part_id>)`. Re-run; the prompt self-corrects within `retries=4`. Switching to `MODEL=gpt-4o` removes the flake. |
| Empty / non-grounded output | The corpus isn't ingested into your tenant. Run `make seed-unified-corpus PARENT_FOLDER_ID=<uuid>`. |
| `Connection error` from OpenAI | Transient; retry. |
| `request_limit of 50` exceeded | The agent looped too many tools. Re-run; this is rare. |

#### Files

```text
recipes/vendor_consolidation/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## vendor_security_review

> Source: [`recipes/vendor_security_review`](../../../recipes/vendor_security_review)

### Vendor Security Review

> **Vendor security review — vendor name + category → cited risk memo.**

#### Table of contents

1. [What this recipe does](#what-this-recipe-does)
2. [How it works](#how-it-works)
3. [Sign in to Knowledge Stack](#sign-in-to-knowledge-stack)
4. [Ingest the unified corpus](#ingest-the-unified-corpus)
5. [Inputs](#inputs)
6. [Output schema](#output-schema)
7. [Run](#run)
8. [Live verified output](#live-verified-output)
9. [Troubleshooting](#troubleshooting)
10. [Files](#files)

#### What this recipe does

Pain point: Every new vendor kicks off a 3rd-party risk review. Security
teams want a consistent first draft grounded in the company's vendor-mgmt,
breach-response, and data-protection policies.

Framework: pydantic-ai. KS access via the knowledgestack-mcp stdio server.
Output: stdout (JSON).

#### How it works

1. The recipe spawns the `knowledgestack-mcp` stdio server (auth via `KS_API_KEY`).
2. A pydantic-ai `Agent` is built with a strict pydantic output schema and `gpt-4o`/`gpt-4o-mini`.
3. The agent asks Knowledge Stack natural-language questions via `search_knowledge`. **It never passes folder UUIDs** — KS finds the right document by content.
4. For every search hit the agent calls `read(path_part_id=<hit>)` to retrieve the full chunk text. The trailing `[chunk:<uuid>]` marker is the citation.
5. The validated pydantic object is printed as JSON to stdout. Every `chunk_id` is a verbatim UUID from a real chunk in your tenant.

#### Sign in to Knowledge Stack

**Path A — `ingestion: true` (shared cookbook tenant, fastest)**

Sign in at <https://app.knowledgestack.ai>, request a read-only "Cookbook demo" key, then:

```bash
export KS_API_KEY=sk-user-...
export KS_BASE_URL=https://api.knowledgestack.ai
export OPENAI_API_KEY=sk-...
export MODEL=gpt-4o-mini
```

Skip to step 5 (Run).

**Path B — `ingestion: false` (clone repo, ingest into your own tenant)**

```bash
git clone https://github.com/knowledgestack/ks-cookbook
cd ks-cookbook
make install
export KS_API_KEY=sk-user-...   # your own KS key
export KS_BASE_URL=https://api.knowledgestack.ai
export OPENAI_API_KEY=sk-...
export MODEL=gpt-4o-mini
```

#### Ingest the unified corpus

Path B only — one-time. The bundled `seed/` folder has 34 real public-domain documents (CMS ICD-10, NIST 800-53, IRS Pubs, OCC Handbook, KO 10-K, AAPL 2024 proxy, FAR, NERC CIP, FDA Orange Book, BLS XLSX, CDC PPTX, …). Create a parent folder in your tenant via the UI, then:

```bash
make seed-unified-corpus PARENT_FOLDER_ID=<your-folder-uuid>
```

#### Inputs

| Flag | Type | Required | Default | Help |
|---|---|---|---|---|

| `--vendor` | str | yes | — | Vendor company name. |

| `--category` | str | no | 'data processor' | e.g. data processor, payment processor, hosting. |

#### Output schema

`VendorReview` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `vendor` | `str` |

| `category` | `str` |

| `risks` | `list[RiskItem]` |

| `recommendation` | `str` |

| `rationale` | `str` |

#### Run

```bash
uv run python recipes/vendor_security_review/recipe.py \
    --vendor "Acme Vendor LLC"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~25.0s):

```json
{
  "vendor": "Acme Vendor LLC",
  "category": "data processor",
  "risks": [
    {
      "risk": "Inadequate vendor management policies may lead to security lapses during data processing.",
      "severity": "high",
      "mitigation": "Es
```

Every `chunk_id` is a verbatim UUID from a `[chunk:<uuid>]` marker; snippets and document names are real chunk content from the ingested corpus.

#### Troubleshooting

| Symptom | Fix |
|---|---|
| `Set KS_API_KEY and OPENAI_API_KEY.` | Export both env vars before running. |
| `Tool 'read' exceeded max retries` | gpt-4o-mini occasionally calls `read(<chunk_id>)` instead of `read(<path_part_id>)`. Re-run; the prompt self-corrects within `retries=4`. Switching to `MODEL=gpt-4o` removes the flake. |
| Empty / non-grounded output | The corpus isn't ingested into your tenant. Run `make seed-unified-corpus PARENT_FOLDER_ID=<uuid>`. |
| `Connection error` from OpenAI | Transient; retry. |
| `request_limit of 50` exceeded | The agent looped too many tools. Re-run; this is rare. |

#### Files

```text
recipes/vendor_security_review/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## version_drift_review

> Source: [`recipes/version_drift_review`](../../../recipes/version_drift_review)

### Version Drift Review

> **Version drift review — summarize changes across document versions and flag regressions (controls weakened vs. a prior version) with chunk citations.**

#### Table of contents

1. [What this recipe does](#what-this-recipe-does)
2. [How it works](#how-it-works)
3. [Sign in to Knowledge Stack](#sign-in-to-knowledge-stack)
4. [Ingest the unified corpus](#ingest-the-unified-corpus)
5. [Inputs](#inputs)
6. [Output schema](#output-schema)
7. [Run](#run)
8. [Live verified output](#live-verified-output)
9. [Troubleshooting](#troubleshooting)
10. [Files](#files)

#### What this recipe does

Pain point: A policy was tightened in v2, then quietly loosened in v3. Nobody
noticed until an audit. This recipe lists every version of a document, pulls
each version's chunks (with real chunk IDs), and asks an LLM to produce a cited
changelog plus a list of *regressions* — changes that weaken a control.

Framework: pydantic-ai + ksapi SDK (the MCP v1 `read` tool only returns the
current version, so historical versions are fetched via the SDK; citations are
still real chunk UUIDs from the backend).
Tools used: SDK list_document_versions, SDK get_document_version_contents.
Output: file (version-drift.md).

Companion: ``seed.py`` creates a demo Access Control Policy with three versions
whose drift is deliberately engineered (v2 tightens, v3 regresses).

#### How it works

1. The recipe spawns the `knowledgestack-mcp` stdio server (auth via `KS_API_KEY`).
2. A pydantic-ai `Agent` is built with a strict pydantic output schema and `gpt-4o`/`gpt-4o-mini`.
3. The agent asks Knowledge Stack natural-language questions via `search_knowledge`. **It never passes folder UUIDs** — KS finds the right document by content.
4. For every search hit the agent calls `read(path_part_id=<hit>)` to retrieve the full chunk text. The trailing `[chunk:<uuid>]` marker is the citation.
5. The validated pydantic object is printed as JSON to stdout. Every `chunk_id` is a verbatim UUID from a real chunk in your tenant.

#### Sign in to Knowledge Stack

**Path A — `ingestion: true` (shared cookbook tenant, fastest)**

Sign in at <https://app.knowledgestack.ai>, request a read-only "Cookbook demo" key, then:

```bash
export KS_API_KEY=sk-user-...
export KS_BASE_URL=https://api.knowledgestack.ai
export OPENAI_API_KEY=sk-...
export MODEL=gpt-4o-mini
```

Skip to step 5 (Run).

**Path B — `ingestion: false` (clone repo, ingest into your own tenant)**

```bash
git clone https://github.com/knowledgestack/ks-cookbook
cd ks-cookbook
make install
export KS_API_KEY=sk-user-...   # your own KS key
export KS_BASE_URL=https://api.knowledgestack.ai
export OPENAI_API_KEY=sk-...
export MODEL=gpt-4o-mini
```

#### Ingest the unified corpus

Path B only — one-time. The bundled `seed/` folder has 34 real public-domain documents (CMS ICD-10, NIST 800-53, IRS Pubs, OCC Handbook, KO 10-K, AAPL 2024 proxy, FAR, NERC CIP, FDA Orange Book, BLS XLSX, CDC PPTX, …). Create a parent folder in your tenant via the UI, then:

```bash
make seed-unified-corpus PARENT_FOLDER_ID=<your-folder-uuid>
```

#### Inputs

| Flag | Type | Required | Default | Help |
|---|---|---|---|---|

| `--doc-id` | str | yes | — | Document ID (run seed.py to create a demo). |

| `--out` | str | no | — |  |

#### Output schema

`DriftReport` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `summary` | `str` |

| `changes` | `list[str]` |

| `regressions` | `list[Regression]` |

#### Run

```bash
uv run python recipes/version_drift_review/recipe.py \
    --doc-id "demo" \
    --out "demo"
```

#### Live verified output

⚠️ **Last verification (fail, 1.1s)** — see `e2e_recipes_merged.json` for full stderr. This recipe is currently a known-issue; see [`docs/RFC_KS_MCP_HANDHOLDING.md`](../../docs/RFC_KS_MCP_HANDHOLDING.md) for the upstream fix that unblocks small-model first-shot pass rate.

#### Troubleshooting

| Symptom | Fix |
|---|---|
| `Set KS_API_KEY and OPENAI_API_KEY.` | Export both env vars before running. |
| `Tool 'read' exceeded max retries` | gpt-4o-mini occasionally calls `read(<chunk_id>)` instead of `read(<path_part_id>)`. Re-run; the prompt self-corrects within `retries=4`. Switching to `MODEL=gpt-4o` removes the flake. |
| Empty / non-grounded output | The corpus isn't ingested into your tenant. Run `make seed-unified-corpus PARENT_FOLDER_ID=<uuid>`. |
| `Connection error` from OpenAI | Transient; retry. |
| `request_limit of 50` exceeded | The agent looped too many tools. Re-run; this is rare. |

#### Files

```text
recipes/version_drift_review/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## well_log_summarizer

> Source: [`recipes/well_log_summarizer`](../../../recipes/well_log_summarizer)

### Well Log Summarizer

> **Well-log / drilling-report summarizer — well ID → cited HSE + ops summary.**

#### Table of contents

1. [What this recipe does](#what-this-recipe-does)
2. [How it works](#how-it-works)
3. [Sign in to Knowledge Stack](#sign-in-to-knowledge-stack)
4. [Ingest the unified corpus](#ingest-the-unified-corpus)
5. [Inputs](#inputs)
6. [Output schema](#output-schema)
7. [Run](#run)
8. [Live verified output](#live-verified-output)
9. [Troubleshooting](#troubleshooting)
10. [Files](#files)

#### What this recipe does

Pain point: Drilling engineers triage 100s of daily drilling reports and well
logs. This recipe scans your corpus (DOE OpenEnergy + SPE papers + state RRC
filings), pulls HSE events, equipment issues, and formation notes, and emits
a cited summary so hazards aren't buried in 40-page PDFs.

Framework: pydantic-ai. Tools: list_contents, search_knowledge, read.
Output: stdout (JSON).

#### How it works

1. The recipe spawns the `knowledgestack-mcp` stdio server (auth via `KS_API_KEY`).
2. A pydantic-ai `Agent` is built with a strict pydantic output schema and `gpt-4o`/`gpt-4o-mini`.
3. The agent asks Knowledge Stack natural-language questions via `search_knowledge`. **It never passes folder UUIDs** — KS finds the right document by content.
4. For every search hit the agent calls `read(path_part_id=<hit>)` to retrieve the full chunk text. The trailing `[chunk:<uuid>]` marker is the citation.
5. The validated pydantic object is printed as JSON to stdout. Every `chunk_id` is a verbatim UUID from a real chunk in your tenant.

#### Sign in to Knowledge Stack

**Path A — `ingestion: true` (shared cookbook tenant, fastest)**

Sign in at <https://app.knowledgestack.ai>, request a read-only "Cookbook demo" key, then:

```bash
export KS_API_KEY=sk-user-...
export KS_BASE_URL=https://api.knowledgestack.ai
export OPENAI_API_KEY=sk-...
export MODEL=gpt-4o-mini
```

Skip to step 5 (Run).

**Path B — `ingestion: false` (clone repo, ingest into your own tenant)**

```bash
git clone https://github.com/knowledgestack/ks-cookbook
cd ks-cookbook
make install
export KS_API_KEY=sk-user-...   # your own KS key
export KS_BASE_URL=https://api.knowledgestack.ai
export OPENAI_API_KEY=sk-...
export MODEL=gpt-4o-mini
```

#### Ingest the unified corpus

Path B only — one-time. The bundled `seed/` folder has 34 real public-domain documents (CMS ICD-10, NIST 800-53, IRS Pubs, OCC Handbook, KO 10-K, AAPL 2024 proxy, FAR, NERC CIP, FDA Orange Book, BLS XLSX, CDC PPTX, …). Create a parent folder in your tenant via the UI, then:

```bash
make seed-unified-corpus PARENT_FOLDER_ID=<your-folder-uuid>
```

#### Inputs

| Flag | Type | Required | Default | Help |
|---|---|---|---|---|

| `--well-id` | str | yes | — | API well number or operator well name. |

#### Output schema

`WellSummary` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `well_id` | `str` |

| `operator` | `str` |

| `depth_summary` | `str` |

| `events` | `list[WellEvent]` |

| `recommended_actions` | `list[str]` |

#### Run

```bash
uv run python recipes/well_log_summarizer/recipe.py \
    --well-id "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~19.8s):

```json
{
  "well_id": "demo",
  "operator": "Demo Operator",
  "depth_summary": "The well demo currently has no reported HSE incidents. Equipment issues are also not highlighted in the recent reports.",
  "events": [
    {
      "event_type": "hse
```

Every `chunk_id` is a verbatim UUID from a `[chunk:<uuid>]` marker; snippets and document names are real chunk content from the ingested corpus.

#### Troubleshooting

| Symptom | Fix |
|---|---|
| `Set KS_API_KEY and OPENAI_API_KEY.` | Export both env vars before running. |
| `Tool 'read' exceeded max retries` | gpt-4o-mini occasionally calls `read(<chunk_id>)` instead of `read(<path_part_id>)`. Re-run; the prompt self-corrects within `retries=4`. Switching to `MODEL=gpt-4o` removes the flake. |
| Empty / non-grounded output | The corpus isn't ingested into your tenant. Run `make seed-unified-corpus PARENT_FOLDER_ID=<uuid>`. |
| `Connection error` from OpenAI | Transient; retry. |
| `request_limit of 50` exceeded | The agent looped too many tools. Re-run; this is rare. |

#### Files

```text
recipes/well_log_summarizer/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

