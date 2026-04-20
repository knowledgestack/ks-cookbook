# nda_review

Triages an inbound NDA against your data-handling/retention policies and emits a structured `NDAReview` (clause flags + severity + policy citation + recommendation).

```bash
uv run python recipes/nda_review/recipe.py --counterparty "Acme Vendor"
uv run python recipes/nda_review/recipe.py --nda-file ./inbound.txt
```

Framework: pydantic-ai with structured output.
