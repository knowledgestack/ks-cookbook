# Sample visit inputs

Use with `make demo-chiro-autopilot`:

1. **Low-back pain with radicular symptoms (prior auth likely):**
   - `PATIENT_ID=PT-4401`
   - `VISIT_DATE=2026-04-18`

2. **Whiplash after MVA (MVA coverage + prior auth):**
   - `PATIENT_ID=PT-5120`
   - `VISIT_DATE=2026-04-15`

3. **Wellness maintenance visit (no prior auth, self-pay):**
   - `PATIENT_ID=PT-3301`
   - `VISIT_DATE=2026-04-19`

Output: three artifacts in `flagships/chiro_visit_autopilot/`:
- `sample_output_coding.xlsx` — billable lines with row-level fee citations
- `sample_output_prior_auth.docx` — payer-ready letter (when required)
- `sample_output_patient_plan.md` — plain-language plan-of-care
