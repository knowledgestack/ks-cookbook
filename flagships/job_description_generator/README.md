# HR: Job Description Generator

Role title → full JD grounded in leveling criteria + comp bands.

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
