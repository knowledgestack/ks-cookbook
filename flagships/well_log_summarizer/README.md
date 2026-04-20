# Energy: Well-Log Summarizer


**Tags:** `energy` `oil-gas` `drilling` `hse`

Drilling engineers triage hundreds of daily reports and mud logs per pad.
This flagship pulls HSE events, equipment issues, and formation notes from
every relevant document in the corpus and produces a one-page, fully-cited
well summary with an HSE risk rating.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** operator daily drilling reports, mudlogs, state RRC
completion filing, one or two SPE papers on the target formation.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `ENERGY_CORPUS_FOLDER_ID=<your-folder-id> make demo-well-log`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
make demo-well-log   # defaults: WELL_ID="42-255-31234"
```

Output: `sample_output.md` — well metadata, depth + formation summary,
classified event list (hse / equipment / formation / lost_time) with
severities and per-event citations, an HSE risk rating, and recommended
actions.

## Data sources

Seed with public data only:

- **US DOE OpenEnergy** — sample drilling reports
  (https://openei.org/)
- **Texas Railroad Commission** — completion filings W-2 / W-1
  (https://rrc.texas.gov/oil-and-gas/)
- **SPE OnePetro** — public-access formation papers
  (https://onepetro.org/)

## Framework

**pydantic-ai** with a strict `WellSummary` result type. Every `WellEvent`
must carry ≥1 citation whose `chunk_id` was copied verbatim from a
`[chunk:<uuid>]` marker in the `read` output.

## Related recipe

A ≤100-LOC recipe version lives at
[`recipes/well_log_summarizer/`](../../recipes/well_log_summarizer/) for
copy-paste reuse.
