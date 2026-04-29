# Recipes Q-T

_Generated. Do not edit by hand._

[← Back to recipes book](../recipes.md)

## qbr_deck_outline

> Source: [`recipes/qbr_deck_outline`](../../../recipes/qbr_deck_outline)

### Qbr Deck Outline

> **QBR deck outline — customer → cited outline for a quarterly business review.**

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

Pain point: CSMs rebuild the same QBR deck every quarter from scratch. This
recipe produces a slide-level outline (agenda, wins, risks, roadmap tie-ins,
asks) with citations per slide from past QBRs and success plans.

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

| `--quarter` | str | no | 'Q2 2026' |  |

#### Output schema

`QBROutline` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `account` | `str` |

| `quarter` | `str` |

| `slides` | `list[Slide]` |

| `asks` | `list[str]` |

#### Run

```bash
uv run python recipes/qbr_deck_outline/recipe.py \
    --account "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~29.2s):

```json
{
  "account": "demo",
  "quarter": "Q2 2026",
  "slides": [
    {
      "title": "Agenda",
      "bullets": [
        "Wins",
        "Usage & Adoption",
        "Open Risks",
        "KS Workflow"
      ],
      "citations": []
    },
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
recipes/qbr_deck_outline/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## regulations_comment_summarizer

> Source: [`recipes/regulations_comment_summarizer`](../../../recipes/regulations_comment_summarizer)

### Regulations Comment Summarizer

> **Regulations.gov comment summarizer — docket → cited theme summary.**

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

Pain point: Regulatory affairs staff skim thousands of public comments on a
proposed rule. This recipe clusters comments from your ingested docket and
returns a cited theme summary with representative excerpts.

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

| `--docket-id` | str | yes | — | e.g. 'EPA-HQ-OAR-2026-0123' |

#### Output schema

`CommentSummary` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `docket_id` | `str` |

| `total_comments_estimate` | `str` |

| `themes` | `list[Theme]` |

#### Run

```bash
uv run python recipes/regulations_comment_summarizer/recipe.py \
    --docket-id "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~18.5s):

```json
{
  "docket_id": "demo",
  "total_comments_estimate": "0",
  "themes": [
    {
      "theme": "Example Theme 1",
      "stance": "support",
      "representative_quote": "This is a quote supporting the initiative.",
      "approximate_count
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
recipes/regulations_comment_summarizer/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## renewal_risk_evidence

> Source: [`recipes/renewal_risk_evidence`](../../../recipes/renewal_risk_evidence)

### Renewal Risk Evidence

> **Renewal risk evidence pack — customer + renewal date → cited evidence bundle.**

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

Pain point: Renewal committees ask "what's the evidence this will or won't
renew?" and CSMs scramble. This recipe returns a structured evidence pack
(value realized, adoption, open risks, exec advocacy) with citations.

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

| `--renewal-date` | str | yes | — | YYYY-MM-DD |

#### Output schema

`RenewalEvidence` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `account` | `str` |

| `renewal_date` | `str` |

| `recommendation` | `str` |

| `value_realized` | `EvidenceSection` |

| `adoption` | `EvidenceSection` |

| `open_risks` | `EvidenceSection` |

| `exec_advocacy` | `EvidenceSection` |

#### Run

```bash
uv run python recipes/renewal_risk_evidence/recipe.py \
    --account "demo" \
    --renewal-date "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~50.4s):

```json
{
  "account": "demo",
  "renewal_date": "2026-04-28T18:00:26.931144+00:00",
  "recommendation": "at_risk",
  "value_realized": {
    "title": "Value Realized for Demo Account",
    "bullets": [
      "SUMMARY PENDING",
      "Asset impairm
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
recipes/renewal_risk_evidence/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## resume_jd_scorer

> Source: [`recipes/resume_jd_scorer`](../../../recipes/resume_jd_scorer)

### Resume Jd Scorer

> **Resume-to-JD scorer — resume text + role → cited fit score with bias guards.**

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

Pain point: Recruiters skim 200 resumes per req. This recipe scores fit vs
the JD from your corpus (must-have + nice-to-have), and filters evidence
that is *not* job-relevant (name, age, graduation year, employment gaps) to
reduce bias.

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

| `--resume-file` | str | yes | — |  |


**Sample inputs available** in `sample_inputs/`:

- `resume_swe_backend.txt`

#### Output schema

`ResumeScore` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `role` | `str` |

| `fit_score` | `int` |

| `criteria` | `list[CriterionHit]` |

| `non_job_factors_ignored` | `list[str]` |

#### Run

```bash
uv run python recipes/resume_jd_scorer/recipe.py \
    --role "Backend Engineer" \
    --resume-file recipes/resume_jd_scorer/sample_inputs/resume_swe_backend.txt
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~22.6s):

```json
{
  "role": "demo",
  "fit_score": 80,
  "criteria": [
    {
      "criterion": "Experience with backend development in Python and event-driven architectures",
      "type": "must_have",
      "verdict": "hit",
      "evidence_in_resume": "
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
recipes/resume_jd_scorer/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

└── sample_inputs/

    └── resume_swe_backend.txt

```

---

## rfp_question_router

> Source: [`recipes/rfp_question_router`](../../../recipes/rfp_question_router)

### Rfp Question Router

> **RFP question router — RFP line → cited team owner + draft answer.**

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

Pain point: RFP questions land in one big doc; half should go to Security,
half to Engineering, the rest to PMM. This recipe routes each question to the
right team and drafts a cited first answer from your corpus.

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

`RoutedAnswer` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `question` | `str` |

| `owner_team` | `str` |

| `confidence` | `str` |

| `draft_answer` | `str` |

| `needs_human_review_reason` | `str` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/rfp_question_router/recipe.py \
    --question "What ERISA disclosures must an employer provide to participants in the SPD?"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~25.6s):

```json
{
  "question": "What ERISA disclosures must an employer provide to participants in the SPD?",
  "owner_team": "Legal",
  "confidence": "high",
  "draft_answer": "Employers must provide the following ERISA disclosures in the Summary Plan De
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
recipes/rfp_question_router/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## runway_scenario

> Source: [`recipes/runway_scenario`](../../../recipes/runway_scenario)

### Runway Scenario

> **Runway scenario — scenario name → cited cash runway table with assumptions.**

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

Pain point: FP&A rebuilds runway scenarios every board cycle. This recipe
reads the latest plan doc + actuals summary and produces a cited scenario
(baseline / downside / upside) with runway months.

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

| `--scenario` | str | yes | — |  |

#### Output schema

`RunwayScenario` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `scenario` | `str` |

| `starting_cash` | `str` |

| `monthly_burn` | `str` |

| `runway_months` | `int` |

| `assumptions` | `list[Assumption]` |

#### Run

```bash
uv run python recipes/runway_scenario/recipe.py \
    --scenario baseline
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~191.7s):

```json
{
  "scenario": "baseline",
  "starting_cash": "not in corpus \u2014 upload data to proceed",
  "monthly_burn": "not in corpus \u2014 upload data to proceed",
  "runway_months": 0,
  "assumptions": [
    {
      "driver": "financial project
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
recipes/runway_scenario/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## samgov_rfp_match

> Source: [`recipes/samgov_rfp_match`](../../../recipes/samgov_rfp_match)

### Samgov Rfp Match

> **SAM.gov RFP match notifier — capability keywords → cited matching opportunities.**

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

Pain point: GovCon BD teams scan SAM.gov daily for matching opportunities.
This recipe reads the ingested notices corpus and returns a ranked list of
matches with NAICS, response-by, and fit rationale.

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

| `--capabilities` | str | yes | — | Comma-separated, e.g. 'RAG,citations,PII redaction'. |

#### Output schema

`RFPMatchReport` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `capabilities` | `list[str]` |

| `matches` | `list[Opportunity]` |

#### Run

```bash
uv run python recipes/samgov_rfp_match/recipe.py \
    --capabilities "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~12.5s):

```json
{
  "capabilities": [
    "demo"
  ],
  "matches": [
    {
      "notice_id": "123456",
      "title": "Small Business Innovation Research (SBIR) Program",
      "agency": "Department of Defense",
      "naics": "541715",
      "response_by
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
recipes/samgov_rfp_match/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## sdlc_checklist

> Source: [`recipes/sdlc_checklist`](../../../recipes/sdlc_checklist)

### Sdlc Checklist

> **Pre-merge SDLC checklist — given a PR description, return required steps.**

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

Pain point: Every engineer needs to remember threat-model review, data-class
check, licence scan, etc. for certain PR kinds. This recipe reads the SDLC
policy and emits the PR-specific checklist with citations.

Framework: LangGraph + MCP adapters (showcases yet another framework).

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

| `--pr` | str | yes | — | PR description (markdown or plain). |

#### Output schema

Output is JSON printed to stdout.

#### Run

```bash
uv run python recipes/sdlc_checklist/recipe.py \
    --pr "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~12.0s):

```json
{
  "checklist_markdown": "Based on the company\u2019s SDLC and data protection policies, here is a checklist of pre-merge actions required for the PR-1234:\n\n### Pre-Merge Checklist for PR-1234\n\n1. **Review Security and Privacy Requirem
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
recipes/sdlc_checklist/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## security_awareness_quiz

> Source: [`recipes/security_awareness_quiz`](../../../recipes/security_awareness_quiz)

### Security Awareness Quiz

> **Security awareness quiz — audience → cited 10-question quiz from policy.**

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

Pain point: Annual security training quizzes become stale copy-paste. This
recipe generates a fresh, policy-grounded quiz (MCQ + short answer) with
citations so learners can click through to the source.

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

| `--audience` | str | no | 'all employees' |  |

#### Output schema

`Quiz` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `audience` | `str` |

| `questions` | `list[Question]` |

#### Run

```bash
uv run python recipes/security_awareness_quiz/recipe.py
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~33.5s):

```json
{
  "audience": "all employees",
  "questions": [
    {
      "prompt": "What is the primary purpose of using strong passwords in workplace security?",
      "format": "mcq",
      "choices": [
        "To impress colleagues",
        "To p
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
recipes/security_awareness_quiz/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## security_finding_triage

> Source: [`recipes/security_finding_triage`](../../../recipes/security_finding_triage)

### Security Finding Triage

> **Security finding triage — scanner finding → cited triage verdict.**

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

Pain point: SAST/DAST/SCA drop hundreds of findings. Security engineers
re-triage noise. This recipe classifies a finding (true/likely/false positive),
maps it to policy/exception rules, and produces a cited verdict.

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

| `--id` | str | yes | — |  |

| `--description` | str | yes | — |  |

#### Output schema

`TriageVerdict` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `finding_id` | `str` |

| `classification` | `str` |

| `severity` | `str` |

| `policy_exception_applies` | `bool` |

| `remediation` | `str` |

| `sla_days` | `int` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/security_finding_triage/recipe.py \
    --id "demo" \
    --description "Client dinner at Smith & Wollensky NYC"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~31.1s):

```json
{
  "finding_id": "ID-2025-0042",
  "classification": "true_positive",
  "severity": "medium",
  "policy_exception_applies": false,
  "remediation": "Ensure that the dinner follows the rules outlined for business meals, including having a s
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
recipes/security_finding_triage/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## seo_outline_drafter

> Source: [`recipes/seo_outline_drafter`](../../../recipes/seo_outline_drafter)

### Seo Outline Drafter

> **SEO outline drafter — keyword → cited SEO outline (H1/H2, intent, FAQs).**

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

Pain point: SEO teams write outlines by scraping SERPs; brand voice and proof
come later. This recipe seeds the outline from your own corpus so the draft
is brand-correct from minute one, with citations.

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

| `--keyword` | str | yes | — |  |

#### Output schema

`SEOOutline` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `keyword` | `str` |

| `search_intent` | `str` |

| `h1` | `str` |

| `h2s` | `list[str]` |

| `faqs` | `list[FAQ]` |

| `internal_link_suggestions` | `list[str]` |

#### Run

```bash
uv run python recipes/seo_outline_drafter/recipe.py \
    --keyword "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~38.0s):

```json
{
  "keyword": "demo",
  "search_intent": "informational",
  "h1": "Understanding the Concept of Demo",
  "h2s": [
    "What is a Demo?",
    "Different Types of Demos",
    "How Demos are Used in Marketing",
    "The Role of Demos in Produ
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
recipes/seo_outline_drafter/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## sla_breach_report

> Source: [`recipes/sla_breach_report`](../../../recipes/sla_breach_report)

### Sla Breach Report

> **SLA breach report — customer + period → cited SLA breach summary + credits.**

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

Pain point: Customer Success preps SLA credit calculations manually. This
recipe reads the MSA + SLA schedule, computes applicable credit per breach
reference, and cites policy.

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

| `--period` | str | no | 'Q1 2026' |  |

#### Output schema

`SLABreachReport` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `customer` | `str` |

| `period` | `str` |

| `breaches` | `list[Breach]` |

| `total_credit_pct` | `float` |

| `cap_applies` | `bool` |

| `narrative` | `str` |

#### Run

```bash
uv run python recipes/sla_breach_report/recipe.py \
    --customer "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~31.2s):

```json
{
  "customer": "demo",
  "period": "Q1 2026",
  "breaches": [
    {
      "incident_ref": "SLA Credit Limit",
      "metric": "Credit",
      "target": "Maximum allowance when the credit rate is over 20%",
      "observed": "$2,000",
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
recipes/sla_breach_report/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## soc2_evidence

> Source: [`recipes/soc2_evidence`](../../../recipes/soc2_evidence)

### Soc2 Evidence

> **SOC 2 evidence puller — given a control ID, dump cited policy excerpts.**

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

Pain point: Audit prep means hunting through policy PDFs for the paragraphs
that satisfy each Trust Services Criteria control (CC6.1, CC7.2, etc.).
This recipe: control ID → markdown evidence pack with [chunk:<uuid>] tags.

Framework: MCP-only (no LLM). Pure keyword search + read, deterministic.
Tools used: search_keyword, read.
Output: file (soc2-evidence.md).

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

| `--control` | str | no | 'CC6.1' |  |

| `--out` | str | no | 'soc2-evidence.md' | Output markdown file. |

#### Output schema

Output is JSON printed to stdout.

#### Run

```bash
uv run python recipes/soc2_evidence/recipe.py
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~1.8s):

```json
{
  "status": "ok",
  "wrote": "soc2-evidence.md",
  "excerpts": 0
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
recipes/soc2_evidence/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## sprint_planner

> Source: [`recipes/sprint_planner`](../../../recipes/sprint_planner)

### Sprint Planner

> **Sprint planner — backlog + capacity → cited draft sprint plan.**

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

Pain point: every sprint planning meeting re-debates priority, capacity,
and carry-over from scratch because nobody re-reads the last retros. This
recipe pulls the backlog + last-sprint retro + planning policy from KS,
and emits an ordered plan with size/owner hints and risk callouts. Every
line carries a citation.

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

| `--team` | str | yes | — |  |

| `--sprint` | str | yes | — | Sprint identifier, e.g. 2026-S08. |

| `--capacity-days` | str | yes | — |  |

#### Output schema

`SprintPlan` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `team` | `str` |

| `sprint` | `str` |

| `capacity_days` | `int` |

| `committed_items` | `list[PlannedItem]` |

| `stretch_items` | `list[PlannedItem]` |

| `carryover_from_last_sprint` | `list[str]` |

| `risks` | `list[str]` |

| `retro_themes_addressed` | `list[str]` |

#### Run

```bash
uv run python recipes/sprint_planner/recipe.py \
    --team "demo" \
    --sprint FY26-Q2-S1 \
    --capacity-days 10
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~35.5s):

```json
{
  "team": "platform",
  "sprint": "FY26-Q2-S1",
  "capacity_days": 10,
  "committed_items": [
    {
      "rank": 1,
      "title": "Establish shared understanding of workload and team roles",
      "size": "M",
      "owner_hint": "<unas
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
recipes/sprint_planner/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## sre_runbook_gap_check

> Source: [`recipes/sre_runbook_gap_check`](../../../recipes/sre_runbook_gap_check)

### Sre Runbook Gap Check

> **SRE runbook gap check — service → cited gaps vs runbook template.**

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

Pain point: Runbooks exist for some services, not others; quality varies. This
recipe compares an existing service's runbook coverage against your template
(alerts → steps → escalation → rollback) and flags missing sections.

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

| `--service` | str | yes | — |  |

#### Output schema

`GapReport` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `service` | `str` |

| `sections` | `list[SectionStatus]` |

| `top_fixes` | `list[str]` |

#### Run

```bash
uv run python recipes/sre_runbook_gap_check/recipe.py \
    --service "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~45.3s):

```json
{
  "service": "ingest-api",
  "sections": [
    {
      "section": "Overview of Ingest API",
      "present": true,
      "quality": "weak",
      "note": "Insufficient detailed information directly about the ingest API.",
      "citation"
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
recipes/sre_runbook_gap_check/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## stakeholder_map_drafter

> Source: [`recipes/stakeholder_map_drafter`](../../../recipes/stakeholder_map_drafter)

### Stakeholder Map Drafter

> **Stakeholder map drafter — account → cited stakeholder map with roles.**

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

Pain point: Deal reviews ask "who is the champion, who's the blocker, who's
the economic buyer?" and AEs guess. This recipe pulls every named person
mentioned in account notes, classifies their role and influence, and cites.

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

`StakeholderMap` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `account` | `str` |

| `stakeholders` | `list[Stakeholder]` |

| `gaps` | `list[str]` |

#### Run

```bash
uv run python recipes/stakeholder_map_drafter/recipe.py \
    --account "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~20.1s):

```json
{
  "account": "demo",
  "stakeholders": [
    {
      "name": "Business Team",
      "title": "Business Analyst",
      "role": "user",
      "sentiment": "supportive",
      "last_touch": "2026-04-28",
      "citation": {
        "chunk_i
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
recipes/stakeholder_map_drafter/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## support_macro_drafter

> Source: [`recipes/support_macro_drafter`](../../../recipes/support_macro_drafter)

### Support Macro Drafter

> **Support macro drafter — common ticket type → cited macro + escalation path.**

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

Pain point: Support agents write the same reply 50 times before someone turns
it into a macro. This recipe produces a cited macro from your KB, plus the
escalation path for the edge cases.

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

| `--ticket-type` | str | yes | — | e.g. 'API key rotation request' |

#### Output schema

`SupportMacro` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `ticket_type` | `str` |

| `greeting` | `str` |

| `body` | `str` |

| `when_to_use` | `str` |

| `when_not_to_use` | `str` |

| `escalation_path` | `list[str]` |

| `citations` | `list[Citation]` |

#### Run

```bash
uv run python recipes/support_macro_drafter/recipe.py \
    --ticket-type "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~18.4s):

```json
{
  "ticket_type": "demo",
  "greeting": "Welcome to the demo support!",
  "body": "This is a demonstration response for ticket handling. Company will make reasonable efforts to provide technical support to customers during regular business
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
recipes/support_macro_drafter/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## symptom_triage

> Source: [`recipes/symptom_triage`](../../../recipes/symptom_triage)

### Symptom Triage

> **Symptom triage — patient-reported symptoms → cited triage bucket.**

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

Pain point: Front-desk intake routes patients to the right level of care
(self-care / telehealth / same-day / urgent / ED). This recipe returns a
cited triage per your protocol corpus. Not a diagnosis tool.

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

| `--symptoms` | str | yes | — |  |

#### Output schema

`TriageOutcome` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `presenting_symptoms` | `str` |

| `red_flags` | `list[str]` |

| `disposition` | `str` |

| `time_to_care` | `str` |

| `rationale` | `str` |

| `citations` | `list[Citation]` |

| `disclaimer` | `str` |

#### Run

```bash
uv run python recipes/symptom_triage/recipe.py \
    --symptoms "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~4.6s):

```json
{
  "presenting_symptoms": "demo",
  "red_flags": [],
  "disposition": "self_care",
  "time_to_care": "N/A",
  "rationale": "Insufficient specific symptoms provided for evaluation.",
  "citations": [
    {
      "chunk_id": "not in corpus \
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
recipes/symptom_triage/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## tech_debt_ledger

> Source: [`recipes/tech_debt_ledger`](../../../recipes/tech_debt_ledger)

### Tech Debt Ledger

> **Tech debt ledger — area keyword → cited prioritized tech-debt list.**

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

Pain point: Tech debt lives in Slack threads and retros, never in a ledger. By
review time nobody remembers what to pay down. This recipe mines your retros /
design docs for debt items, ranks by severity, and cites sources.

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

| `--area` | str | yes | — | e.g. 'ingestion pipeline' |

#### Output schema

`DebtLedger` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `area` | `str` |

| `items` | `list[DebtItem]` |

#### Run

```bash
uv run python recipes/tech_debt_ledger/recipe.py \
    --area "demo"
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~37.1s):

```json
{
  "area": "demo",
  "items": [
    {
      "title": "Product Vulnerability and Defects in Hardware/Software",
      "impact": "high",
      "effort": "M",
      "description": "Our complex hardware and software products may contain defect
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
recipes/tech_debt_ledger/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

```

---

## title_defect_spotter

> Source: [`recipes/title_defect_spotter`](../../../recipes/title_defect_spotter)

### Title Defect Spotter

> **Title-defect spotter — recorded-deed text → cited defect list.**

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

Pain point: Title examiners read chains of deeds, mortgages, liens, judgments
and hunt for breaks (missing signatures, wrong legal description, open liens).
This recipe surfaces candidate defects with citations.

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

| `--parcel` | str | yes | — |  |

| `--chain-file` | str | yes | — |  |


**Sample inputs available** in `sample_inputs/`:

- `title_chain_001.txt`

#### Output schema

`TitleReport` — pydantic model emitted as JSON to stdout.

| Field | Type |
|---|---|

| `parcel` | `str` |

| `defects` | `list[Defect]` |

| `overall_marketability` | `str` |

#### Run

```bash
uv run python recipes/title_defect_spotter/recipe.py \
    --parcel "demo" \
    --chain-file recipes/title_defect_spotter/sample_inputs/title_chain_001.txt
```

#### Live verified output

Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** with `MODEL=gpt-4o-mini` (~16.6s):

```json
{
  "parcel": "demo",
  "defects": [
    {
      "type": "chain_break",
      "description": "2002 Grant Deed missing trustee acknowledgment; only signed by Robert Holloway as 'trustee,' but trust originally had two trustees.",
      "sever
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
recipes/title_defect_spotter/
├── README.md            ← you are here
├── recipe.py            ← agent + schema (no FOLDER_ID env vars)

└── sample_inputs/

    └── title_chain_001.txt

```

---

