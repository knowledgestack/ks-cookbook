# Prior-authorization letter drafter


**Tags:** `healthcare` `prior-auth` `payer` `clinical`

Turn a patient's clinical scenario + requested service into a **cited prior-auth
or appeal letter** grounded in the health plan's medical-policy bulletins and
the provider-appeal style guide.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Payer medical policy, clinical guidelines, prior-auth letter template.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-prior-auth`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
# Seed the sample Acme Health Plan corpus once:
uv run --env-file ../../ks-backend/.env.e2e python ../../ks-backend/seed/seed_healthcare_corpus.py
export CORPUS_FOLDER_ID="<printed by the seed script>"

make demo-prior-auth
```

Output: `prior-auth-letter.docx` containing the full letter with inline
`[chunk:<uuid>]` citations copied verbatim from the plan's MPBs.

## Framework

Uses **pydantic-ai** with `result_type=PriorAuthLetter` — the agent MUST
return a validated pydantic model or the run fails.

## Guardrails

- Every citation is copied verbatim from a `[chunk:<uuid>]` marker in the tool
  output. The agent never fabricates UUIDs.
- If retrieved policies do not support medical necessity, the letter
  explicitly states which criterion is not yet met.
