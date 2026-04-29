# Recipes A-D

_Generated. Do not edit by hand._

[← Back to recipes book](../recipes.md)

## access_review

> Source: [`recipes/access_review`](../../../recipes/access_review)

### Access Review

> **Access review — given a user/role/system tuple, judge it against access policies.**

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

Pain point: Quarterly user access reviews are a slog; reviewers don't recall
which policy says "no shared service accounts" or "least privilege for prod".
This recipe: access scenario in → structured judgment with policy citations.

Framework: pydantic-ai with a structured ``AccessReview`` result.
Tools used: list_contents, read.
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

| `--user` | str | no | 'contractor-svc-shared' | User or service account. |

| `--system` | str | no | 'prod-postgres-primary' |  |

| `--role` | str | no | 'superuser write' |  |

#### Output schema

`AccessReview` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `user` | `str` |

| `system` | `str` |

| `role` | `str` |

| `verdict` | `str` |

| `rationale` | `str` |

| `findings` | `list[str]` |

| `policy_refs` | `list[Citation]` |

#### Run

```bash
uv run python recipes/access_review/recipe.py
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~18.8s):

```json
{
  "user": "contractor-svc-shared",
  "system": "prod-postgres-primary",
  "role": "superuser write",
  "verdict": "approve",
  "rationale": "Access rights under the 'contractor-svc-shared' role align with the guidelines for contractor acc
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
recipes/access_review/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## account_research_brief

> Source: [`recipes/account_research_brief`](../../../recipes/account_research_brief)

### Account Research Brief

> **Account research brief — account name → cited pre-call prep sheet.**

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

Pain point: AEs rebuild the same prep doc for every call: past touchpoints,
product fit, objections, champion map. This recipe pulls it from your corpus
(call notes, past proposals, product docs) with chunk citations.

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

| `--account` | str | yes | — |  |

#### Output schema

`AccountBrief` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `account` | `str` |

| `summary` | `str` |

| `recent_activity` | `list[str]` |

| `known_objections` | `list[str]` |

| `product_fit` | `list[str]` |

| `recommended_next_step` | `str` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/account_research_brief/recipe.py \
    --account "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~24.5s):

```json
{
  "account": "demo",
  "summary": "The recent activity includes various documents related to financial transactions and presentations that outline significant details regarding different entities.",
  "recent_activity": [
    "Review of l
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
recipes/account_research_brief/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## adr_drafter

> Source: [`recipes/adr_drafter`](../../../recipes/adr_drafter)

### Adr Drafter

> **Architecture Decision Record drafter grounded in security/eng policies.**

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

Pain point: Engineers write ADRs from a blank page; constraint references
(data-classification, encryption, vendor-mgmt) are forgotten until review.
This recipe asks Knowledge Stack about your engineering / security policies
and produces ADR markdown with policy-cited constraints in the "Policy
Constraints" section.

Framework: pydantic-ai. KS access via the knowledgestack-mcp stdio server.
Output: file (adr.md by default).

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

| `--decision` | str | no | 'Adopt managed Postgres for the analytics service' |  |

| `--context` | str | no | 'Current self-hosted Postgres has frequent on-call pages.' |  |

| `--out` | str | no | 'adr.md' |  |

#### Output schema

`ADR` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `title` | `str` |

| `status` | `str` |

| `context` | `str` |

| `decision` | `str` |

| `consequences` | `list[str]` |

| `policy_constraints` | `list[PolicyConstraint]` |

#### Run

```bash
uv run python recipes/adr_drafter/recipe.py
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~106.2s):

```json
{
  "title": "Adopt Managed Postgres for Analytics Service",
  "status": "Proposed",
  "context": "The current self-hosted Postgres has frequent on-call pages, indicating a need for more reliable database management. Adopting a managed Post
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
recipes/adr_drafter/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## aml_sar_narrative

> Source: [`recipes/aml_sar_narrative`](../../../recipes/aml_sar_narrative)

### Aml Sar Narrative

> **AML SAR narrative writer — case → cited FinCEN-format SAR narrative.**

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

Pain point: AML analysts hand-write 200-word Suspicious Activity Report
narratives in FinCEN's Who/What/When/Where/Why/How format. This recipe asks
Knowledge Stack about the case (transaction ledger exports, alert rationale,
KYC notes, FinCEN guidance) and drafts a compliant narrative grounded in
real chunks of those documents.

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

| `--case-id` | str | yes | — | AML case identifier or distinguishing keyword. |

#### Output schema

`SARNarrative` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `case_id` | `str` |

| `who` | `str` |

| `what` | `str` |

| `when` | `str` |

| `where` | `str` |

| `why_suspicious` | `str` |

| `how` | `str` |

| `narrative` | `str` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/aml_sar_narrative/recipe.py \
    --case-id structuring-cash-deposits
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~21.1s):

```json
{
  "case_id": "structuring-cash-deposits",
  "who": "Subject's name and identifying details not provided in corpus.",
  "what": "Suspicious activity related to cash deposits possibly structured to evade reporting requirements.",
  "when":
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
recipes/aml_sar_narrative/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## analyst_inquiry_responder

> Source: [`recipes/analyst_inquiry_responder`](../../../recipes/analyst_inquiry_responder)

### Analyst Inquiry Responder

> **Analyst inquiry responder — analyst question → cited talking points.**

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

Pain point: Gartner / Forrester / IDC inquiries come with precise questions;
you have 30 minutes to prep. This recipe builds a talking-point sheet with
cited evidence from product docs, case studies, and customer proof.

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

| `--question` | str | yes | — |  |

#### Output schema

`AnalystPrep` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `analyst_question` | `str` |

| `headline_answer` | `str` |

| `talking_points` | `list[str]` |

| `proof_points` | `list[str]` |

| `anticipated_followups` | `list[str]` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/analyst_inquiry_responder/recipe.py \
    --question "What ERISA disclosures must an employer provide to participants in the SPD?"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~23.3s):

```json
{
  "analyst_question": "What ERISA disclosures must an employer provide to participants in the SPD?",
  "headline_answer": "Employers must provide various disclosures under ERISA, including summary plan descriptions, summaries of material
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
recipes/analyst_inquiry_responder/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## api_deprecation_notice

> Source: [`recipes/api_deprecation_notice`](../../../recipes/api_deprecation_notice)

### Api Deprecation Notice

> **API deprecation notice — endpoint → cited customer-facing deprecation notice.**

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

Pain point: Deprecations are communicated inconsistently. This recipe asks
Knowledge Stack about your team's deprecation conventions (header format,
minimum notice window, communication template) and your API reference, then
drafts a standard notice with real citations.

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

| `--endpoint` | str | yes | — | e.g. POST /v1/ingest |

| `--replacement` | str | yes | — | e.g. POST /v2/ingest |

| `--sunset` | str | yes | — | YYYY-MM-DD |

#### Output schema

`DeprecationNotice` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `endpoint` | `str` |

| `deprecation_reason` | `str` |

| `replacement` | `str` |

| `sunset_date` | `str` |

| `migration_steps` | `list[str]` |

| `header_to_watch` | `str` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/api_deprecation_notice/recipe.py \
    --endpoint "POST /v1/ingest" \
    --replacement "POST /v2/ingest" \
    --sunset 2026-12-31
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~27.6s):

```json
{
  "endpoint": "POST /v1/ingest",
  "deprecation_reason": "The /v1/ingest API endpoint will be deprecated in favor of the new /v2/ingest endpoint, which includes improved functionality and performance enhancements.",
  "replacement": "POST
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
recipes/api_deprecation_notice/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## basel_iii_risk_weight

> Source: [`recipes/basel_iii_risk_weight`](../../../recipes/basel_iii_risk_weight)

### Basel Iii Risk Weight

> **Basel III risk-weight calculator — exposure → cited RWA calculation.**

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

Pain point: Credit risk teams look up Basel III risk weights manually (by
asset class, counterparty type, CRM). This recipe reads the Basel III rules
from your corpus and computes the risk-weighted asset (RWA) with citations.

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

| `--name` | str | yes | — | Exposure label. |

| `--asset-class` | str | yes | — |  |

| `--counterparty` | str | yes | — |  |

| `--notional` | str | yes | — |  |

#### Output schema

`RWACalculation` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `exposure_name` | `str` |

| `asset_class` | `str` |

| `counterparty_type` | `str` |

| `notional` | `str` |

| `applied_risk_weight_pct` | `float` |

| `rwa` | `str` |

| `crm_applied` | `str` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/basel_iii_risk_weight/recipe.py \
    --name "Acme Corp" \
    --asset-class corporate \
    --counterparty "BB-rated corporate" \
    --notional 10000000
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~11.7s):

```json
{
  "exposure_name": "Acme Corp",
  "asset_class": "corporate",
  "counterparty_type": "BB-rated corporate",
  "notional": "10000000",
  "applied_risk_weight_pct": 150.0,
  "rwa": "15000000",
  "crm_applied": "none",
  "citations": [
    {
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
recipes/basel_iii_risk_weight/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## bcp_drill_plan

> Source: [`recipes/bcp_drill_plan`](../../../recipes/bcp_drill_plan)

### Bcp Drill Plan

> **Business continuity drill plan grounded in BCP/DR policies.**

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

Pain point: Annual BCP/DR tabletops need a custom scenario, success criteria,
and references to your real recovery objectives — but they get copy-pasted
from last year and slowly drift from policy.

Framework: pydantic-ai. KS access via the knowledgestack-mcp stdio server.
Output: stdout (JSON) + file (drill-plan.md).

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

| `--scenario` | str | no | 'Primary region outage: us-east-1 unavailable for 4 hours.' |  |

| `--out` | str | no | 'drill-plan.md' |  |

#### Output schema

`DrillPlan` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `scenario` | `str` |

| `participants` | `list[str]` |

| `timeline` | `list[Inject]` |

| `success_criteria` | `list[SuccessCriterion]` |

| `policy_references` | `list[Citation]` |

#### Run

```bash
uv run python recipes/bcp_drill_plan/recipe.py
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~14.9s):

```json
{
  "scenario": "Primary region outage: us-east-1 unavailable for 4 hours.",
  "participants": [
    "IT Department",
    "Disaster Recovery Team",
    "Incident Response Team",
    "Management",
    "Communications Team"
  ],
  "timeline":
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
recipes/bcp_drill_plan/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## benefits_enrollment_qa

> Source: [`recipes/benefits_enrollment_qa`](../../../recipes/benefits_enrollment_qa)

### Benefits Enrollment Qa

> **Benefits enrollment Q&A — question → cited answer from SPDs + carrier docs.**

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

Pain point: Open enrollment: employees ask the same 50 questions about HDHP
vs PPO, HSA rules, coverage abroad, dependent age cutoffs. This recipe asks
Knowledge Stack about the question and grounds the answer in real chunks
of your Summary Plan Descriptions / carrier docs.

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

| `--question` | str | yes | — | Employee benefits question, e.g. 'When can I change my HSA contribution?' |

#### Output schema

`BenefitsAnswer` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `question` | `str` |

| `answer` | `str` |

| `plan_specific` | `bool` |

| `contact_for_edge_case` | `str` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/benefits_enrollment_qa/recipe.py \
    --question "What ERISA disclosures must an employer provide to participants in the SPD?"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~21.8s):

```json
{
  "question": "What ERISA disclosures must an employer provide to participants in the SPD?",
  "answer": "Employers must provide several ERISA disclosures to participants, including: \n\n1. **Summary Plan Description (SPD)**: The SPD info
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
recipes/benefits_enrollment_qa/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## board_update_drafter

> Source: [`recipes/board_update_drafter`](../../../recipes/board_update_drafter)

### Board Update Drafter

> **Board update drafter — period → cited board update draft.**

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

Pain point: Founders write the monthly update from scratch, every time. This
recipe produces a structured draft (highlights, KPIs, risks, asks) grounded
in your OKR tracker, sales notes, and incident list with citations.

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

| `--period` | str | no | 'March 2026' |  |

#### Output schema

`BoardUpdate` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `period` | `str` |

| `tl_dr` | `str` |

| `highlights` | `list[str]` |

| `kpis` | `list[str]` |

| `risks` | `list[str]` |

| `asks` | `list[str]` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/board_update_drafter/recipe.py
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~44.2s):

```json
{
  "period": "March 2026",
  "tl_dr": "March 2026 highlights include significant investments in innovative technology and community partnerships, with solid financial KPIs reported for major companies. Risks involve geopolitical tensions a
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
recipes/board_update_drafter/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## case_study_drafter

> Source: [`recipes/case_study_drafter`](../../../recipes/case_study_drafter)

### Case Study Drafter

> **Case study drafter — customer → cited case-study draft.**

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

Pain point: Case studies are bottlenecked on PMM. Customer notes and metrics
live across QBRs and call transcripts. This recipe assembles a structured
draft (challenge, solution, results) with chunk citations.

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

| `--customer` | str | yes | — |  |

#### Output schema

`CaseStudyDraft` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `customer` | `str` |

| `hero_stat` | `str` |

| `challenge` | `str` |

| `solution` | `str` |

| `results` | `list[str]` |

| `pull_quote` | `str` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/case_study_drafter/recipe.py \
    --customer "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~215.9s):

```json
{
  "customer": "demo",
  "hero_stat": "(not in corpus \u2014 upload data to proceed)",
  "challenge": "(not in corpus \u2014 upload data to proceed)",
  "solution": "(not in corpus \u2014 upload data to proceed)",
  "results": [
    "(not
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
recipes/case_study_drafter/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## cashflow_anomaly_detector

> Source: [`recipes/cashflow_anomaly_detector`](../../../recipes/cashflow_anomaly_detector)

### Cashflow Anomaly Detector

> **Cash-flow anomaly detector — bank CSV path → cited anomaly list.**

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

Pain point: Controllers reconcile bank statements line by line and miss
unusual patterns (duplicate vendors, weekend ACH bursts, above-threshold
cash withdrawals). This recipe scans the CSV for anomalies and asks
Knowledge Stack about your AP/AR notes + expense / treasury policy to
ground each suggested control in real chunks of those documents.

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

| `--csv` | str | yes | — | Path to bank transaction CSV. |


**Sample inputs available** in `sample_inputs/`:

- `bank_txns_2025_q1.csv`

#### Output schema

`AnomalyReport` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `source_csv` | `str` |

| `anomalies` | `list[Anomaly]` |

#### Run

```bash
uv run python recipes/cashflow_anomaly_detector/recipe.py \
    --csv recipes/cashflow_anomaly_detector/sample_inputs/bank_txns_2025_q1.csv
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~31.6s):

```json
{
  "source_csv": "bank_txns_2025_q1.csv",
  "anomalies": [
    {
      "pattern": "Duplicate vendor payments detected.",
      "example_lines": [
        "2025-01-02,ACH PAYMENT,-12450.00,Acme Vendor LLC,Operating,Invoice #INV-7811",
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
recipes/cashflow_anomaly_detector/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

└── sample_inputs/

    └── bank_txns_2025_q1.csv

```

---

## change_management_review

> Source: [`recipes/change_management_review`](../../../recipes/change_management_review)

### Change Management Review

> **Change management review — proposed change → cited policy-gate checklist.**

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

Pain point: Every PR/deploy that touches prod should map to your change-mgmt
policy (peer review, ticket, rollback plan, off-hours window for risky
changes). Engineers forget the gates; reviewers re-derive them each time.

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

| `--change` | str | no | 'Drop-and-recreate the orders.user_id index in prod Postgres' |  |

| `--risk` | str | no | 'high' |  |

#### Output schema

`ChangeReview` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `change` | `str` |

| `risk_level` | `str` |

| `gates` | `list[PolicyGate]` |

#### Run

```bash
uv run python recipes/change_management_review/recipe.py
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~17.3s):

```json
{
  "change": "Drop-and-recreate the orders.user_id index in prod Postgres",
  "risk_level": "high",
  "gates": [
    {
      "gate": "Limit access to authorized personnel for changes.",
      "why": "Access restrictions help prevent unauth
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
recipes/change_management_review/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## change_monitor_to_pr

> Source: [`recipes/change_monitor_to_pr`](../../../recipes/change_monitor_to_pr)

### Change Monitor To Pr

> **Change monitor → PR body recipe.**

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

Title: Watch a KS corpus for material changes and emit a PR-ready diff summary.
Tenant: any seeded tenant with a watched corpus.
Framework: raw MCP via _shared.mcp_client.
Pain point: engineers / compliance teams hand-roll scripts that watch
            regulatory filings, vendor API docs, or case law and file PRs
            when something changes (see HN 'What are you working on', 2026).

Keeps under 100 LOC. Stateless on the client side — uses KS chunk UUIDs as
the change-tracking key.

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

| `--folder-id` | str | no | — |  |

| `--topic` | str | yes | — | Search query to watch, e.g. 'SOC 2 CC6.1'. |

| `--snapshot` | str | no | — |  |

| `--out` | str | no | — |  |

#### Output schema

Output is JSON printed to stdout.

#### Run

```bash
uv run python recipes/change_monitor_to_pr/recipe.py \
    --folder-id "demo" \
    --topic "Q4 board update" \
    --snapshot "demo" \
    --out "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~2.0s):

```json
{
  "topic": "Q4 board update",
  "tracked_chunks": 5,
  "changes": [
    {
      "type": "added",
      "chunk_id": "019cffb7-228b-7ee0-ba96-1a8abf91c0b6",
      "document": "Knowledge Stack - Company Overview.pptx",
      "snippet": "Apri
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
recipes/change_monitor_to_pr/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## changelog_from_commits

> Source: [`recipes/changelog_from_commits`](../../../recipes/changelog_from_commits)

### Changelog From Commits

> **Changelog from commits — commit summaries → cited user-facing changelog.**

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

Pain point: Engineers write dense commits; users need the "what changed,
why you care" version. This recipe takes raw commit messages and asks
Knowledge Stack about your product docs / security policies for context,
then produces a Keep-A-Changelog–style entry list with citations where
the change touches documented behavior.

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

| `--version` | str | yes | — |  |

| `--date` | str | yes | — |  |

| `--commits-file` | str | yes | — | Text file with commit subjects (one per line). |


**Sample inputs available** in `sample_inputs/`:

- `commits_v2_4_0.txt`

#### Output schema

`Changelog` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `version` | `str` |

| `date` | `str` |

| `entries` | `list[ChangelogEntry]` |

#### Run

```bash
uv run python recipes/changelog_from_commits/recipe.py \
    --version v2.4.0 \
    --date 2026-04-27 \
    --commits-file recipes/changelog_from_commits/sample_inputs/commits_v2_4_0.txt
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~16.2s):

```json
{
  "version": "v2.4.0",
  "date": "2026-04-27",
  "entries": [
    {
      "category": "Added",
      "summary": "Introduced a new /v2/ingest endpoint with support for batch uploads.",
      "why_user_cares": "Users can now upload multiple
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
recipes/changelog_from_commits/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

└── sample_inputs/

    └── commits_v2_4_0.txt

```

---

## churn_risk_flags

> Source: [`recipes/churn_risk_flags`](../../../recipes/churn_risk_flags)

### Churn Risk Flags

> **Churn risk flags — customer → risk signals from QBRs, tickets, usage notes.**

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

Pain point: CSMs don't know which accounts are quietly slipping until renewal
slips. This recipe surfaces cited risk signals (usage decline mentions, exec
sponsor loss, competitive evals) with severity + next action.

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

| `--account` | str | yes | — |  |

#### Output schema

`ChurnReport` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `account` | `str` |

| `overall_risk` | `str` |

| `signals` | `list[RiskSignal]` |

| `recommended_play` | `str` |

#### Run

```bash
uv run python recipes/churn_risk_flags/recipe.py \
    --account "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~18.7s):

```json
{
  "account": "demo",
  "overall_risk": "medium",
  "signals": [
    {
      "signal": "System interruptions impact service availability",
      "severity": "medium",
      "evidence": "We experience occasional system interruptions and del
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
recipes/churn_risk_flags/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## citizen_intent_311

> Source: [`recipes/citizen_intent_311`](../../../recipes/citizen_intent_311)

### Citizen Intent 311

> **311 citizen-intent router — citizen message → cited department + SLA.**

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

Pain point: 311 call centers triage thousands of messages daily into the right
city department. This recipe classifies intent per your service catalog and
returns owner + SLA + follow-up template with citations.

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

| `--message` | str | yes | — |  |

#### Output schema

`IntentRoute` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `message` | `str` |

| `intent_category` | `str` |

| `department` | `str` |

| `urgency` | `str` |

| `sla_hours` | `int` |

| `followup_template` | `str` |

| `citation` | `Citation` |

#### Run

```bash
uv run python recipes/citizen_intent_311/recipe.py \
    --message "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~11.7s):

```json
{
  "message": "The search returned various items related to the term \"demo.\" These include images and text from documents related to user interfaces, examples used in publications, and icons typically utilized in software applications. S
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
recipes/citizen_intent_311/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## clause_extractor

> Source: [`recipes/clause_extractor`](../../../recipes/clause_extractor)

### Clause Extractor

> **Clause extractor — contract name → cited inventory of standard clauses.**

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

Pain point: Legal ops needs to know "does this contract have a limitation of
liability cap? indemnity? IP assignment? auto-renew?" across hundreds of
documents. This recipe runs against your Knowledge Stack tenant — drop your
contracts in via the KS UI, then run this and you get a structured clause
inventory grounded in real chunk citations.

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

| `--contract` | str | yes | — | Contract name or distinguishing keyword that appears in the document filename or content. |

#### Output schema

`ClauseInventory` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `contract` | `str` |

| `clauses` | `list[ClauseHit]` |

#### Run

```bash
uv run python recipes/clause_extractor/recipe.py \
    --contract "Apple 2024 proxy"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~66.7s):

```json
{
  "contract": "Apple 2024 Proxy",
  "clauses": [
    {
      "clause": "limitation of liability",
      "present": false,
      "excerpt": "not found",
      "citation": {
        "chunk_id": "",
        "document_name": "",
        "snip
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
recipes/clause_extractor/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## cloud_cost_anomaly

> Source: [`recipes/cloud_cost_anomaly`](../../../recipes/cloud_cost_anomaly)

### Cloud Cost Anomaly

> **Cloud cost anomaly explainer — AWS CUR CSV → cited anomaly explanations.**

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

Pain point: FinOps sees a $40k NAT-gateway spike; explaining it takes a
half day of Slack spelunking. This recipe scans the CUR extract, then asks
Knowledge Stack about cloud cost optimization patterns, deploy notes, and
runbooks to ground the likely cause and recommended action.

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

| `--period` | str | no | 'March 2026' |  |

| `--cur-file` | str | yes | — | AWS Cost-and-Usage Report extract (CSV). |


**Sample inputs available** in `sample_inputs/`:

- `aws_cur_march_2026.csv`

#### Output schema

`CostReport` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `period` | `str` |

| `anomalies` | `list[CostAnomaly]` |

#### Run

```bash
uv run python recipes/cloud_cost_anomaly/recipe.py \
    --cur-file recipes/cloud_cost_anomaly/sample_inputs/aws_cur_march_2026.csv
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~64.0s):

```json
{
  "period": "March 2026",
  "anomalies": [
    {
      "service": "EC2",
      "usage_type": "BoxUsage:c6i.4xlarge",
      "delta": "$14170.55",
      "likely_cause": "Ensuring that everything you pay for is used and avoiding significantl
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
recipes/cloud_cost_anomaly/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

└── sample_inputs/

    └── aws_cur_march_2026.csv

```

---

## coa_mapper

> Source: [`recipes/coa_mapper`](../../../recipes/coa_mapper)

### Coa Mapper

> **Chart-of-accounts mapper — source COA CSV → cited target-system mapping.**

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

Pain point: Migrating QuickBooks → NetSuite (or any re-chart) means mapping
every account by hand. This recipe reads both chart docs from your corpus and
emits a line-by-line mapping with confidence and a citation for each.

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

| `--csv` | str | yes | — | CSV of source account numbers + names. |

| `--source` | str | no | 'QuickBooks' |  |

| `--target` | str | no | 'NetSuite' |  |


**Sample inputs available** in `sample_inputs/`:

- `source_accounts.csv`

#### Output schema

`COAMap` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `source_system` | `str` |

| `target_system` | `str` |

| `mappings` | `list[AccountMapping]` |

#### Run

```bash
uv run python recipes/coa_mapper/recipe.py \
    --csv recipes/coa_mapper/sample_inputs/source_accounts.csv
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~60.4s):

```json
{
  "source_system": "QuickBooks",
  "target_system": "NetSuite",
  "mappings": [
    {
      "source_account": "1010",
      "target_account": "Cash and Cash Equivalents",
      "confidence": "high",
      "reason": "Cash is typically cate
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
recipes/coa_mapper/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

└── sample_inputs/

    └── source_accounts.csv

```

---

## compensation_band_check

> Source: [`recipes/compensation_band_check`](../../../recipes/compensation_band_check)

### Compensation Band Check

> **Compensation band check — role + level + location → cited band + verdict.**

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

Pain point: Recruiters ping Total Rewards for every offer: "is $X for Staff SWE
in NYC in band?". This recipe looks up the band doc and returns a cited verdict
with band min / mid / max and any location adjustment.

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

| `--role` | str | yes | — |  |

| `--level` | str | yes | — |  |

| `--location` | str | yes | — |  |

| `--proposed` | str | yes | — | Proposed base salary. |

#### Output schema

`BandCheck` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `role` | `str` |

| `level` | `str` |

| `location` | `str` |

| `band_min` | `str` |

| `band_mid` | `str` |

| `band_max` | `str` |

| `location_adjustment` | `str` |

| `proposed` | `str` |

| `verdict` | `str` |

| `rationale` | `str` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/compensation_band_check/recipe.py \
    --role "Backend Engineer" \
    --level "demo" \
    --location "demo" \
    --proposed "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~13.4s):

```json
{
  "role": "demo",
  "level": "demo",
  "location": "demo",
  "band_min": "not in corpus \u2014 upload data to proceed",
  "band_mid": "not in corpus \u2014 upload data to proceed",
  "band_max": "not in corpus \u2014 upload data to procee
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
recipes/compensation_band_check/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## competitive_positioning

> Source: [`recipes/competitive_positioning`](../../../recipes/competitive_positioning)

### Competitive Positioning

> **Competitive positioning — competitor name → cited win/loss positioning sheet.**

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

Pain point: AEs on a live call Slack-ping the PMM team for "how do we position
against X?" every single time. This recipe returns a cited sheet: their
strengths, our counters, traps to avoid.

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

| `--competitor` | str | yes | — |  |

#### Output schema

`Position` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `competitor` | `str` |

| `their_strengths` | `list[str]` |

| `their_weaknesses` | `list[str]` |

| `our_counters` | `list[str]` |

| `traps_to_avoid` | `list[str]` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/competitive_positioning/recipe.py \
    --competitor "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~48.3s):

```json
{
  "competitor": "demo",
  "their_strengths": [
    "User-friendly interface",
    "Advanced segmentation options",
    "Strong policy enforcement mechanisms",
    "Comprehensive operational manuals"
  ],
  "their_weaknesses": [
    "Weak
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
recipes/competitive_positioning/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## construction_rfi_agent

> Source: [`recipes/construction_rfi_agent`](../../../recipes/construction_rfi_agent)

### Construction Rfi Agent

> **Construction RFI / submittal agent — RFI text → cited draft response.**

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

Pain point: RFIs (Requests For Information) pile up on jobsites; answering
each one means cross-referencing CSI MasterFormat specs, ASHRAE + FHWA
standards, drawings, and prior submittals. This recipe drafts a cited first
pass so the PM only spends time on the ambiguous ones.

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

| `--rfi-number` | str | yes | — |  |

| `--text` | str | yes | — | The RFI question body. |

#### Output schema

`RFIDraft` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `rfi_number` | `str` |

| `subject` | `str` |

| `spec_section` | `str` |

| `draft_response` | `str` |

| `schedule_impact_days` | `int` |

| `cost_impact` | `str` |

| `needs_architect_response` | `bool` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/construction_rfi_agent/recipe.py \
    --rfi-number "demo" \
    --text "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~18.4s):

```json
{
  "rfi_number": "RFI-001",
  "subject": "Request for Information on Design Specifications",
  "spec_section": "01 11 00",
  "draft_response": "We appreciate your inquiry regarding the design specifications. Any requests for changes to the
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
recipes/construction_rfi_agent/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## content_brief_drafter

> Source: [`recipes/content_brief_drafter`](../../../recipes/content_brief_drafter)

### Content Brief Drafter

> **Content brief drafter — topic → cited content brief (audience, angle, proof).**

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

Pain point: Writers get a topic and spin their wheels. This recipe produces a
cited brief: target audience, key angle, proof points (from your case studies,
product docs), and recommended structure.

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

| `--topic` | str | yes | — |  |

#### Output schema

`ContentBrief` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `topic` | `str` |

| `audience` | `str` |

| `angle` | `str` |

| `key_messages` | `list[str]` |

| `proof_points` | `list[str]` |

| `outline` | `list[str]` |

| `cta` | `str` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/content_brief_drafter/recipe.py \
    --topic "Q4 board update"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~16.1s):

```json
{
  "topic": "Q4 Board Update",
  "audience": "Board Members and Stakeholders",
  "angle": "Highlighting recent achievements and strategic insights for the upcoming quarter.",
  "key_messages": [
    "Overview of Q4 performance highlights."
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
recipes/content_brief_drafter/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## contract_renewal_checker

> Source: [`recipes/contract_renewal_checker`](../../../recipes/contract_renewal_checker)

### Contract Renewal Checker

> **Contract renewal checker — contract → cited renewal summary + actions.**

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

Pain point: Auto-renewals sneak up; notice windows get missed. This recipe
asks Knowledge Stack about a named contract, extracts term end + renewal
mechanics + fee escalator, and emits a calendar-ready action list with
real citations into the contract document.

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

| `--contract` | str | yes | — | Contract name or distinguishing keyword (e.g. company name). |

#### Output schema

`RenewalCheck` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `contract` | `str` |

| `term_end` | `str` |

| `auto_renews` | `bool` |

| `notice_window_days` | `int` |

| `fee_escalator` | `str` |

| `actions` | `list[RenewalAction]` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/contract_renewal_checker/recipe.py \
    --contract "Apple 2024 proxy"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~22.2s):

```json
{
  "contract": "Apple 2024 proxy",
  "term_end": "2024-01-11",
  "auto_renews": false,
  "notice_window_days": 30,
  "fee_escalator": "TBD",
  "actions": [
    {
      "do_by": "2024-01-01",
      "action": "Send non-renewal notice by the
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
recipes/contract_renewal_checker/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## court_docket_monitor

> Source: [`recipes/court_docket_monitor`](../../../recipes/court_docket_monitor)

### Court Docket Monitor

> **Court-docket monitor — party + period → cited litigation activity summary.**

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

Pain point: Legal + strategy teams want to know "has <competitor> been sued
in N.D. Cal. this quarter?" without paying for PACER monitoring. This
recipe asks Knowledge Stack about the named party's litigation in the
period and returns a cited summary.

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

| `--party` | str | yes | — | Company or individual name. |

| `--period` | str | no | 'Q1 2026' |  |

#### Output schema

`DocketReport` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `party` | `str` |

| `period` | `str` |

| `entries` | `list[DocketEntry]` |

| `headline` | `str` |

#### Run

```bash
uv run python recipes/court_docket_monitor/recipe.py \
    --party "Jackson Women's Health Organization"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~5.4s):

```json
{
  "party": "Jackson Women's Health Organization",
  "period": "Q1 2026",
  "entries": [],
  "headline": "No litigation involving Jackson Women's Health Organization in the corpus for Q1 2026."
}
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
recipes/court_docket_monitor/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## csat_theme_mining

> Source: [`recipes/csat_theme_mining`](../../../recipes/csat_theme_mining)

### Csat Theme Mining

> **CSAT theme mining — period → cited themes from support surveys + tickets.**

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

Pain point: CX leaders skim 500 CSAT comments and recall the last three. This
recipe clusters themes across the corpus (survey exports, ticket summaries),
cites representative chunks, and suggests priority fixes.

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

| `--period` | str | no | 'Q1 2026' |  |

#### Output schema

`ThemeReport` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `period` | `str` |

| `themes` | `list[Theme]` |

| `headline` | `str` |

#### Run

```bash
uv run python recipes/csat_theme_mining/recipe.py
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~25.6s):

```json
{
  "period": "Q1 2026",
  "themes": [
    {
      "theme": "Continuous Improvement Process",
      "sentiment": "positive",
      "frequency_estimate": "high",
      "representative_quote": "Have a process for continuous improvement: Regul
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
recipes/csat_theme_mining/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## data_subject_request_responder

> Source: [`recipes/data_subject_request_responder`](../../../recipes/data_subject_request_responder)

### Data Subject Request Responder

> **Data subject request (DSR) responder — GDPR/CCPA request → cited response plan.**

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

Pain point: A data subject files an access/erasure request. Privacy ops
must confirm the legal basis, pull applicable systems-of-record, quote the
relevant retention/erasure policy, and compose a compliant response. This
recipe asks Knowledge Stack about your privacy policy + retention rules
and grounds every fact in real chunks.

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

| `--type` | str | yes | — |  |

| `--jurisdiction` | str | no | 'GDPR' |  |

| `--subject` | str | no | 'customer (EU, former employee)' |  |

#### Output schema

`DSRResponse` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `request_type` | `str` |

| `jurisdiction` | `str` |

| `response_deadline_days` | `int` |

| `systems_to_query` | `list[str]` |

| `policy_refs` | `list[Citation]` |

| `response_draft` | `str` |

#### Run

```bash
uv run python recipes/data_subject_request_responder/recipe.py \
    --type erasure
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~15.1s):

```json
{
  "request_type": "erasure",
  "jurisdiction": "GDPR",
  "response_deadline_days": 30,
  "systems_to_query": [
    "customer database",
    "HR systems"
  ],
  "policy_refs": [
    {
      "chunk_id": "019dd20b-e699-793e-a607-c6f4f44301b8
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
recipes/data_subject_request_responder/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## deal_loss_retro

> Source: [`recipes/deal_loss_retro`](../../../recipes/deal_loss_retro)

### Deal Loss Retro

> **Deal loss retro — closed-lost deal → cited root causes + playbook deltas.**

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

Pain point: Loss reasons in CRM are one-word garbage ("price"). This recipe
reads the real artifacts (call notes, proposal, email thread summary) and
produces a structured retro with citations — what actually happened and which
playbook step failed.

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

| `--deal` | str | yes | — | Deal / opportunity name. |

#### Output schema

`LossRetro` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `deal` | `str` |

| `lost_to` | `str` |

| `stated_reason` | `str` |

| `actual_root_causes` | `list[str]` |

| `playbook_gaps` | `list[str]` |

| `keep_doing` | `list[str]` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/deal_loss_retro/recipe.py \
    --deal "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~12.3s):

```json
{
  "deal": "demo",
  "lost_to": "not in corpus \u2014 upload data to proceed",
  "stated_reason": "Note: Loss percentages do not sum correctly (intentional error).",
  "actual_root_causes": [
    "Loss percentages did not correctly reflect
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
recipes/deal_loss_retro/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## discharge_summary_rewrite

> Source: [`recipes/discharge_summary_rewrite`](../../../recipes/discharge_summary_rewrite)

### Discharge Summary Rewrite

> **Discharge summary plain-language rewrite — clinical summary → patient version.**

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

Pain point: Discharge summaries are dense jargon; AHRQ says patient-friendly
rewrites reduce readmits. This recipe rewrites at ~6th-grade reading level,
preserves every medication and follow-up, and cites the source sentences.

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

| `--summary-file` | str | yes | — |  |


**Sample inputs available** in `sample_inputs/`:

- `discharge_summary_001.txt`

#### Output schema

`PatientSummary` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `what_happened` | `str` |

| `your_medications` | `list[str]` |

| `follow_ups` | `list[str]` |

| `call_doctor_if` | `list[str]` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/discharge_summary_rewrite/recipe.py \
    --summary-file recipes/discharge_summary_rewrite/sample_inputs/discharge_summary_001.txt
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~33.5s):

```json
{
  "what_happened": "You were admitted to the hospital with chest pain and confirmed to have a type of heart attack called NSTEMI. You were treated with medications and underwent a procedure to open up blocked arteries. You are stable and
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
recipes/discharge_summary_rewrite/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

└── sample_inputs/

    └── discharge_summary_001.txt

```

---

## document_versions

> Source: [`recipes/document_versions`](../../../recipes/document_versions)

### Document Versions

> **Document versions probe — list + diff version metadata for a corpus document.**

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

Pain point: Policies change quarterly. Auditors ask "what changed in v3 of the
access-control policy, and which chunk says so?". Reviewers need a deterministic
way to see version metadata and newest-version chunks without trusting an LLM.

Framework: MCP-only (no LLM). Deterministic.
Tools used: find, get_info, list_contents, read.
Output: file (document-versions.md).

NOTE ON VERSIONING SURFACE. The KS MCP server v1 is read-only. Version *metadata*
is exposed via ``get_info`` / ``list_contents`` (whatever fields the server
returns — this recipe prints them verbatim so you can see the shape). Mutating
version tools (create_version, promote, rollback) are on the roadmap in the
write-back MCP. This recipe is the honest v1 check: it probes what's there and
surfaces citations from the current version's chunks.

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

| `--query` | str | no | 'NIST' | Natural-language query to resolve a document via `find`. |

| `--out` | str | no | — |  |

#### Output schema

Output is JSON printed to stdout.

#### Run

```bash
uv run python recipes/document_versions/recipe.py \
    --out "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~6.1s):

```json
{
  "status": "ok",
  "wrote": "demo"
}
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
recipes/document_versions/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## docx_form_fill

> Source: [`recipes/docx_form_fill`](../../../recipes/docx_form_fill)

### Docx Form Fill

> **DOCX form-fill — replace ``{{placeholders}}`` in a .docx using corpus answers.**

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

Pain point: Vendor questionnaires, DDQs, security forms arrive as Word files with
blanks. Ops copy-pastes from policy PDFs and tracks citations in a sidecar sheet.
This recipe: a ``.docx`` with ``{{field_name}}`` tokens → filled .docx + cited
evidence sidecar (JSON), every answer grounded in real ``[chunk:<uuid>]`` tags.

Framework: pydantic-ai + python-docx.
Tools used: list_contents, search_knowledge, read.
Output: <template-stem>.filled.docx  +  <template-stem>.citations.json

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

| `--template` | str | yes | — | A .docx with {{field_name}} placeholders. |

| `--hint` | str | no | 'Answer from our security & privacy policies.' |  |


**Sample inputs available** in `sample_inputs/`:

- `vendor_w9_template.citations.json`

- `vendor_w9_template.docx`

- `vendor_w9_template.filled.docx`

#### Output schema

`FieldAnswer` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `value` | `str` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/docx_form_fill/recipe.py \
    --template recipes/docx_form_fill/sample_inputs/vendor_w9_template.citations.json
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~208.6s):

```json
{
  "filled_docx": "recipes/docx_form_fill/sample_inputs/vendor_w9_template.filled.docx",
  "citations_json": "recipes/docx_form_fill/sample_inputs/vendor_w9_template.citations.json",
  "fields_filled": 11
}
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
recipes/docx_form_fill/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

└── sample_inputs/

    ├── vendor_w9_template.citations.json

    ├── vendor_w9_template.docx

    └── vendor_w9_template.filled.docx

```

---

## dpa_gap_check

> Source: [`recipes/dpa_gap_check`](../../../recipes/dpa_gap_check)

### Dpa Gap Check

> **DPA gap check — flag missing/weak GDPR clauses vs your data-protection policy.**

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

Pain point: Counterparty Data Processing Addenda often omit standard GDPR
Article 28 obligations. Privacy/legal redoes the same gap analysis each time.
This recipe: DPA text in → list of missing or weak clauses out, each cited
to the company's data-protection policy.

Framework: raw OpenAI chat completions + MCP stdio.
Tools used: list_contents, read.
Output: stdout (markdown).

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

| `--dpa-file` | str | no | — | Path to counterparty DPA text. Default: built-in sample. |


**Sample inputs available** in `sample_inputs/`:

- `vendor_dpa_acme.txt`

#### Output schema

Output is JSON printed to stdout.

#### Run

```bash
uv run python recipes/dpa_gap_check/recipe.py \
    --dpa-file recipes/dpa_gap_check/sample_inputs/vendor_dpa_acme.txt
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~6.7s):

```json
{
  "gap_analysis_markdown": "The DPA provided by the counterparty is not fully compliant with the company's data protection policy. Here are the identified gaps:\n\n- **Purpose Specification** \u2014 The DPA lacks a clear requirement for A
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
recipes/dpa_gap_check/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

└── sample_inputs/

    └── vendor_dpa_acme.txt

```

---

## drug_interaction_checker

> Source: [`recipes/drug_interaction_checker`](../../../recipes/drug_interaction_checker)

### Drug Interaction Checker

> **Drug-drug interaction checker — medication list → cited interaction report.**

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

Pain point: Pharmacists + clinicians cross-check interactions in DailyMed or
Lexicomp. This recipe runs a structured check against your DailyMed-mirrored
corpus and returns interaction severities with citations.

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

| `--meds` | str | yes | — | Comma-separated medications, e.g. 'warfarin,amiodarone,simvastatin' |

#### Output schema

`InteractionReport` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `patient_medications` | `list[str]` |

| `interactions` | `list[Interaction]` |

| `disclaimer` | `str` |

#### Run

```bash
uv run python recipes/drug_interaction_checker/recipe.py \
    --meds "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~4.1s):

```json
{
  "patient_medications": [
    "demo",
    "demo2"
  ],
  "interactions": [],
  "disclaimer": "Decision-support only; verify with a pharmacist."
}
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
recipes/drug_interaction_checker/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

