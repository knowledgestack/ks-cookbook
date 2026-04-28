# Default denial input

Passed as CLI args to `make demo-claims-rebuttal`:

- `PATIENT_ID="PT-9043"`
- `DENIAL_CODE="CO-50"` (not medically necessary)
- `PAYER="BCBS"`
- `SERVICE="Lumbar epidural steroid injection"`
- `PATIENT_CHART_FOLDER_ID=<uuid>`
- `PAYER_POLICY_FOLDER_ID=<uuid>`

The agent opens both corpora in one MCP session, locates the governing
coverage criteria in the payer policy, pulls supporting evidence out of the
chart with `read_around`, and emits a Word appeal letter payer-ready for
submission.
