# Compliance questionnaire demo

Fill a [CAIQ v4](https://cloudsecurityalliance.org/artifacts/cloud-controls-matrix-v4) / SIG-style security questionnaire directly from your KS tenant's policy docs, with citations every auditor can verify.

This is the **HyperComply / SafeBase / Conveyor** use case — an auditor sends an XLSX with 260 control questions, you return the same XLSX filled in with evidence.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** A set of security policy documents (e.g. the open-source JupiterOne policy templates).

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `POLICIES_FOLDER_ID=<your-folder-id> make demo-compliance`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
# One-time: seed the sample corpus (10 JupiterOne policies as "Acme Corp") into your KS tenant
# and print the folder id.
make demo-compliance-setup

# Then fill the first 5 rows of the sample CAIQ:
export POLICIES_FOLDER_ID="<printed by setup>"
make demo-compliance
```

Output: `filled.xlsx` with columns **C (Answer)** and **E (Implementation Description)** populated for each of the 5 (configurable) questions, plus inline `[chunk:<uuid>]` citations an auditor can click through.

## What the agent does per row

1. `list_contents(policies_folder)` — enumerates the 10 policies in your KS tenant.
2. Picks the 1–3 policies whose names match the question (e.g. "access" for authentication questions).
3. `read(path_part_id=<policy>, max_chars=4000)` — pulls the actual policy text with `[chunk:<uuid>]` markers.
4. Emits structured JSON:

   ```json
   {
     "answer": "Yes",
     "description": "Acme Corp restricts logical access via SSO + MFA per the Access Control Policy §3.2.",
     "confidence": "HIGH",
     "citations": [
       {"chunk_id": "5bc91bb6-...", "document_name": "access", "snippet": "Access to all computing resources must be protected by strong authentication..."}
     ]
   }
   ```

5. Writes back into the XLSX preserving the original workbook's formatting.

## Guardrails

- Every HIGH/MEDIUM answer must cite at least one real `chunk_id`.
- If retrieved policies don't ground the question, the agent returns `INSUFFICIENT EVIDENCE` with `LOW` confidence.
- Chunk IDs are copied verbatim from the `read` output — never fabricated.

## Scaling up

- `--limit 260` fills the entire CAIQ (costs ≈ $0.15 on gpt-4o-mini at current rates).
- Swap to Anthropic by setting `COMPLIANCE_PROVIDER=anthropic` + `ANTHROPIC_API_KEY`.
- Bring your own policy corpus: upload docs to any folder in your KS tenant, then set `POLICIES_FOLDER_ID` to that folder's path_part_id.

## Data sources

- Questionnaire: [Texas DPS CAIQ v4.0.2 XLSX](https://www.dps.texas.gov/docs/vendorforms/star-security-questionnaire.xlsx) (state-gov public mirror of the CSA template).
- Policies: [JupiterOne/security-policy-templates](https://github.com/JupiterOne/security-policy-templates) (CC-BY-SA-4.0), rendered for "Acme Corp".
