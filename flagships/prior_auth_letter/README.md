# Prior-authorization letter drafter

Turn a patient's clinical scenario + requested service into a **cited prior-auth
or appeal letter** grounded in the health plan's medical-policy bulletins and
the provider-appeal style guide.

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
