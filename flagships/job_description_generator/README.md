# HR: Job Description Generator

Role title → full JD grounded in leveling criteria + comp bands.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Leveling guide, role framework, comp band overview.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-jd-generator`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
make demo-job-description-generator
```

Or manually:

```bash
ks-cookbook-jd-generator --input --role "Senior Backend Engineer" --level "L5" --corpus-folder $CORPUS_FOLDER_ID --out job_description_generator.md
```

## Corpus

Grounded in: company leveling guide + role framework + comp band overview. Seed with the corresponding `seed_*_corpus.py` script.

## Framework

**pydantic-ai** with structured `JobDescription` output type. Every field cites real chunks from the KS tenant.
