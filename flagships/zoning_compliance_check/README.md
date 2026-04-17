# Zoning Compliance Check (Real Estate)


**Tags:** `real-estate` `zoning` `compliance` `municipal`

Proposed use at a commercial address checked against the City of Austin Land
Development Code (Chapter 25-2) zoning ordinance.

**Framework:** LangGraph ReAct agent with MCP

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Local Land Development Code excerpts, zoning district tables.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-zoning-check`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Data Sources
- Austin TX Land Development Code, Chapter 25-2 (Zoning Districts)
- Austin TX LDC permitted uses table (Subchapter C, Article 2)
- Austin TX LDC conditional use permit process
- Source: https://library.municode.com/tx/austin/codes/land_development_code

## Quick Start

```bash
# 1. Seed the corpus (from ks-backend/)
uv run --env-file .env.e2e python seed/seed_realestate_zoning_corpus.py

# 2. Run the demo (from knowledgestack-cookbook/)
make demo-zoning-check CORPUS_FOLDER_ID=<id-from-step-1>

# Custom scenario:
make demo-zoning-check \
  CORPUS_FOLDER_ID=<id> \
  ADDRESS="500 E 6th St, Austin, TX" \
  ZONE_DISTRICT="CBD" \
  PROPOSED_USE="nightclub"
```

## Output
`zoning-compliance.md` with YES/CONDITIONAL/NO/VARIANCE_REQUIRED determination,
applicable LDC sections, compatibility standards, and next steps.
