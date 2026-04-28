# Unified cookbook corpus

`seed/ingest/` is the **single, real, public-domain corpus** that powers all
152 cookbook use cases. Ingest it once into a Knowledge Stack tenant; every
recipe and flagship then reads against that same tenant via `search_knowledge`
— no per-recipe folder UUIDs, no per-recipe seed.

This is intentional. In production, a Knowledge Stack tenant is a *shared*
knowledge base — engineers, lawyers, finance, and ops all dump their real
documents in, then ask grounded questions. The cookbook mirrors that model.

## What's in here

```
seed/ingest/
├── banking/        FinCEN SAR electronic filing instructions
├── eng/            AWS Well-Architected Framework, NIST SP 800-207 (Zero Trust)
├── energy/         NERC Reliability Standard CIP-002-5.1a
├── finance/        IRS Pub 15, IRS Pub 535, OCC Credit Card Lending,
│                   Coca-Cola 10-K (FY2024), Apple DEF 14A 2024 proxy,
│                   Apple Q4 FY24 earnings statements
├── government/     Federal Acquisition Regulation (FAR), full text
├── healthcare/     CMS FY2026 ICD-10-CM Coding Guidelines,
│                   CMS Medicare Benefit Policy Manual ch. 15
├── hr/             DOL ERISA Reporting & Disclosure Guide for Employee Benefit Plans
├── insurance/      NAIC Model #680 (auto)
├── legal/          SCOTUS Dobbs v. Jackson opinion, USPTO sample utility patent
├── marketing/      FTC Endorsement Guides (16 CFR Part 255)
├── pharma/         FDA Orange Book (Approved Drug Products)
├── policies/       NIST SP 800-53 r5 (Security & Privacy Controls)
└── realestate/     HUD Tenant Rights Lease Addendum
```

**~75 MB across 21 PDFs.** Every file is a real, primary-source document
from a U.S. federal agency or other public-domain source. No markdown stubs.

## How to ingest

```bash
# 1. Sign in at https://app.knowledgestack.ai
# 2. Create a parent folder in your tenant (UI or API), copy its path_part_id
# 3. Run:
KS_API_KEY=sk-user-... KS_BASE_URL=https://api.knowledgestack.ai \
  uv run python scripts/seed_unified_corpus.py \
    --parent-folder-id <PARENT_FOLDER_PATH_PART_ID>
```

The script creates `cookbook-corpus/<vertical>/` under your parent folder,
uploads every PDF in `seed/ingest/<vertical>/`, and waits for KS ingestion
workflows to complete (~4 min per document on hosted KS).

## How recipes use this corpus

Each recipe / flagship calls **`search_knowledge`** (no `path_part_id`) for
every claim it wants to ground. The agent searches the entire tenant, picks
the most relevant chunks, and emits citations of the form
`{chunk_id, document_name, snippet}` where `chunk_id` is a verbatim UUID
from a `[chunk:<uuid>]` marker in the tool output. There are no `*_FOLDER_ID`
env vars in any recipe.

## Adding to the corpus

Drop more public-domain PDFs into `seed/ingest/<vertical>/` and re-run
`seed_unified_corpus.py`. Supported formats: `*.pdf`, `*.docx`, `*.xlsx`,
`*.csv`, `*.html`, `*.txt`.

## Bundled archive (planned)

`make seed-bundle` will produce `seed-cookbook-corpus.zip` so users can
download the whole curated corpus as a single artifact and ingest it into
their own KS tenant. (Pending — see CHANGELOG.)
