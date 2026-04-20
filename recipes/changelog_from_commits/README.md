# changelog_from_commits

Commit list → user-facing changelog. Categorizes (Keep A Changelog style),
writes "why you care", and cites product docs where relevant.

```bash
git log --oneline v0.4.0..HEAD > commits.txt
uv run python recipes/changelog_from_commits/recipe.py \
  --version 0.5.0 --date 2026-04-20 --commits-file commits.txt
```
