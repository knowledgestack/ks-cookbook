# Construction: RFI / Submittal Agent


**Tags:** `construction` `rfi` `submittal` `csi-masterformat` `ashrae`

RFIs pile up on every jobsite — the PM ends the day cross-referencing CSI
spec sections, drawings, and prior submittals to draft one response. This
flagship drafts a first-pass response, identifies the applicable CSI
division, flags whether the architect-of-record needs to weigh in, and
estimates schedule + cost impact — all with citations.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to
create that folder and upload the expected documents **before** running,
otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** project specifications (CSI MasterFormat), issued
drawing set, addenda, prior approved submittals, relevant ASHRAE / FHWA
reference standard excerpts.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CONSTRUCTION_CORPUS_FOLDER_ID=<your-folder-id> make demo-rfi-agent`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
make demo-rfi-agent   # defaults: see sample_inputs/rfi.md
```

Output: `sample_output.md` — restated question, draft response, applicable
CSI spec references (each cited), drawing references, schedule + cost
impact, architect-of-record flag, and the evidence pack.

## Data sources

Seed with project docs (real or fictitious) plus public reference standards:

- **CSI MasterFormat** structure —
  https://www.csiresources.org/standards/masterformat
- **ASHRAE 62.1** ventilation —
  https://www.ashrae.org/technical-resources/standards-and-guidelines
- **FHWA** for civil/transpo projects —
  https://www.fhwa.dot.gov/

Never seed with a client's production drawing set without their permission.

## Framework

**pydantic-ai** with a strict `RFIDraft` result type. Every `SpecReference`
must carry a real citation and the overall `citations` list has a minimum
of 1 entry copied verbatim from a `[chunk:<uuid>]` marker in `read` output.

## Related recipe

A ≤100-LOC recipe version lives at
[`recipes/construction_rfi_agent/`](../../recipes/construction_rfi_agent/).
