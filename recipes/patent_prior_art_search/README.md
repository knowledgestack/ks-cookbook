# patent_prior_art_search

Claim text → cited prior-art candidates with relevance tier (weak / moderate /
strong / anticipating) + novelty-risk verdict.

```bash
uv run python recipes/patent_prior_art_search/recipe.py \
  --claim "A retrieval system that attaches per-chunk citations to generated text..."
```
