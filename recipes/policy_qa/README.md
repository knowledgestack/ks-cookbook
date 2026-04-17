# Policy Q&A

Pain: "#ask-it" slack channel gets the same 20 questions forever.

```bash
uv run python recipes/policy_qa/recipe.py \
  --question "What's our password rotation policy?"
```

Two LLM calls (pick-policy, then answer-from-policy) + one `read` call.
~60 LOC. Shortest possible recipe showing the grounded-RAG pattern.
