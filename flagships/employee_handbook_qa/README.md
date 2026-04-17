# HR: Employee Handbook Q&A

Employee question → cited answer from the company handbook.

## Run

```bash
make demo-employee-handbook-qa
```

Or manually:

```bash
ks-cookbook-handbook-qa --input --question "What is our PTO policy?" --corpus-folder $CORPUS_FOLDER_ID --out employee_handbook_qa.md
```

## Corpus

Grounded in: employee handbook (PTO, remote work, expense, travel, code of conduct). Seed with the corresponding `seed_*_corpus.py` script.

## Framework

**pydantic-ai** with structured `HandbookAnswer` output type. Every field cites real chunks from the KS tenant.
