# Sales: Conversational SDR Bot


**Tags:** `sales` `sdr` `meddic` `discovery` `multi-turn`

A live, multi-turn SDR discovery bot. You type as the prospect; the bot
asks qualifying questions grounded in your product corpus + ICP + past
wins + objection library. At session end it produces a MEDDIC-scored
summary artifact with citations for every claim it made.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to
create that folder and upload the expected documents **before** running,
otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** product one-pager, ICP definition, past-wins library
(≥3 logos with outcomes + metrics), objection-library FAQ, pricing page.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `SALES_CORPUS_FOLDER_ID=<your-folder-id> make demo-sdr-bot`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

```bash
make demo-sdr-bot   # defaults: PROSPECT="Paloma Networks"
```

The bot opens the call. You reply in the terminal. Type `/end` when done.
Output: `sample_output.md` — MEDDIC scorecard (each dimension covered /
partial / missing), discovered pains, metrics, open objections, citations
referenced, and a concrete next step with a time commitment.

## Framework

**pydantic-ai** with multi-turn `message_history`. A second pydantic-ai
agent reruns over the transcript to produce a strict `SessionSummary` —
scoring MEDDIC from the transcript text alone (no optimism bias) and
extracting any `[chunk:<uuid>]` citations that surfaced in the conversation.

## Related

- `flagships/realtime_voice_sdr/` — same pattern, over the OpenAI Realtime
  API, with optional mic/speaker audio.
- Recipes: `meddic_call_coach`, `outbound_call_prep`, `prospecting_email_personalizer`.
