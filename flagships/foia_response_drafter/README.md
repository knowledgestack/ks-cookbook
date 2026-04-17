# Government: FOIA Response Drafter

Drafts a FOIA response letter with exemption analysis citing the DOJ guide
and agency SOP. Uses **raw OpenAI** with inline MCP helpers.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** FOIA statute + exemption guidance, agency records, redaction playbook.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-foia-response`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
# 1. Seed the FOIA corpus
cd ks-backend
uv run --env-file .env.e2e python seed/seed_government_foia_corpus.py

# 2. From the cookbook
cd knowledgestack-cookbook
make demo-foia-response REQUEST="All records related to contract awards for IT services in FY2025"
```

Output: `foia-response.md` with cover letter, exemption analysis, and redaction notes.
