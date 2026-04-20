# Banking: AML SAR Narrative Writer


**Tags:** `banking` `aml` `fincen` `sar` `bsa`

Every bank AML team writes Suspicious Activity Report narratives by hand in
FinCEN's Who/What/When/Where/Why/How format — 200 words per case, hundreds
per quarter. This flagship drafts one automatically from the case evidence,
with a structured ≤200-word narrative, itemized red flags, and a citation
per factual claim.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to
create that folder and upload the expected documents **before** running,
otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** 90 days of transaction ledger exports, alert rationale
memo, subject KYC file, prior SAR history (if any), FFIEC BSA/AML
examination-manual excerpt.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `AML_CORPUS_FOLDER_ID=<your-folder-id> make demo-sar-narrative`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
make demo-sar-narrative   # defaults: CASE_ID="SAR-2026-0417" SUBJECT="Paloma Holdings LLC"
```

Output: `sample_output.md` — subject, filing institution, FinCEN narrative
paragraph, itemized W/W/W/W/W/H fields, red flags, and the evidence pack.

## Data sources

Seed with public guidance + fictitious case data only:

- **FinCEN SAR Narrative guidance** —
  https://www.fincen.gov/sites/default/files/shared/sarnarrcompletguid_web.pdf
- **FFIEC BSA/AML Examination Manual** —
  https://bsaaml.ffiec.gov/manual
- **FinCEN SAR Stats** for red-flag typologies —
  https://www.fincen.gov/reports/sar-stats

Never seed with real customer or production transaction data.

## Framework

**pydantic-ai** with a strict `SARNarrative` result type. Every citation
`chunk_id` must be copied verbatim from a `[chunk:<uuid>]` marker in `read`
output. The 2-citation minimum enforces at least two sources per filing.

## Related recipe

A ≤100-LOC recipe version lives at
[`recipes/aml_sar_narrative/`](../../recipes/aml_sar_narrative/).
