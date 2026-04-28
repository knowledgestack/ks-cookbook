# claims_denial_rebuttal_drafter

Healthcare flagship — generates a payer-ready appeal letter for a denied
claim, grounded in the patient's chart AND the payer's medical policy corpus.

**Market gap.** Payers deny ~15% of claims; ~60% are recoverable but rebuttals
are manual Word-doc work. Existing tools automate coding, not denial response.
This flagship demonstrates two-corpus orchestration (clinical + policy) in a
single Knowledge Stack MCP session, plus `read_around` to pull evidence
passages with enough surrounding context for the letter to read clinically.

**Run:**

```bash
PATIENT_CHART_FOLDER_ID=<uuid> PAYER_POLICY_FOLDER_ID=<uuid> \
  DENIAL_CODE="CO-50" make demo-claims-rebuttal
```
