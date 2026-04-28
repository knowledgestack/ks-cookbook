# Default patient input

Passed as CLI args to `make demo-hcc-coder`:

- `PATIENT_ID="PT-001"`
- `HCC_CORPUS_FOLDER_ID=<your-chart-folder-uuid>`

The corpus should contain progress notes, problem list, and recent labs for
the patient. The agent will enumerate every document and emit an xlsx report
with one row per code — each row carries the exact supporting clinical phrase
and a `[chunk:<uuid>]` citation suitable for CMS audit response.
