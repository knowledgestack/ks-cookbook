# Pre-merge SDLC checklist

Pain: Engineers forget required steps (threat model, licence scan, data-class review)
depending on the PR type.

```bash
uv run python recipes/sdlc_checklist/recipe.py \
  --pr "Adding a new Stripe webhook handler that stores customer payment metadata in Postgres."
```

Uses **LangGraph** ReAct agent + `langchain-mcp-adapters`. Returns a markdown
checklist grounded in the company's SDLC + data-protection policies.
