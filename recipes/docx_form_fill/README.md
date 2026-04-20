# docx_form_fill

**Pain point.** Security questionnaires, vendor DDQs, onboarding forms arrive as
Word templates with blanks. Ops hand-fills them from policy PDFs and tracks
citations in a sidecar spreadsheet.

**What this recipe does.** Reads a `.docx` template that uses `{{field_name}}`
placeholders, asks a pydantic-ai agent to answer each field via the KS MCP
server, writes a filled `.docx`, and emits a `.citations.json` sidecar keyed by
field name with real `[chunk:<uuid>]` citations.

```bash
uv run python recipes/docx_form_fill/recipe.py \
  --template my_questionnaire.docx \
  --hint "Answer from our security and privacy policies"
```

Template authoring: use any Word doc and drop tokens like `{{data_retention}}`,
`{{mfa_enforcement}}`, `{{breach_notification_sla}}`. Keep one token per run
(paragraph-local replacement only; no cross-run token splitting).

Outputs land next to the template:

- `my_questionnaire.filled.docx`
- `my_questionnaire.citations.json`

Citations are never synthesized — every `chunk_id` comes from `read` output.
