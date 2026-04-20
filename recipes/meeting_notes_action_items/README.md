# Meeting notes → action items

One-line pain: after every meeting, someone spends 20 minutes turning the
transcript into a shared doc of decisions, action items, and risks — and
half the items quietly drop.

```bash
uv run python recipes/meeting_notes_action_items/recipe.py \
  --meeting-id "2026-04-17-platform-sync"
```

This recipe reads the meeting transcript (+ optional linked docs) from your
KS corpus, extracts decisions / action items / risks / open questions, and
assigns owners + due dates when they appear in the text. Every item cites
the `[chunk:<uuid>]` it came from.

Framework: pydantic-ai. ≤100 LOC.
