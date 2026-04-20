# interview_competency_grader

Interview transcript + role → per-competency rating (below / meets / exceeds)
citing both rubric text AND specific transcript moments.

```bash
uv run python recipes/interview_competency_grader/recipe.py \
  --role "Staff SWE" --candidate "Alex Kim" --transcript-file transcript.txt
```
