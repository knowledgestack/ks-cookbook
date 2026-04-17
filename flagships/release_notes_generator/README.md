# Engineering/Product: Release Notes Generator

Release tag → customer-facing notes grounded in specs + migration guide.

## Run

```bash
make demo-release-notes-generator
```

Or manually:

```bash
ks-cookbook-release-notes --input --version "v2.4.0" --corpus-folder $CORPUS_FOLDER_ID --out release_notes_generator.md
```

## Corpus

Grounded in: product changelog + feature spec docs + API migration guide. Seed with the corresponding `seed_*_corpus.py` script.

## Framework

**pydantic-ai** with structured `ReleaseNotes` output type. Every field cites real chunks from the KS tenant.
