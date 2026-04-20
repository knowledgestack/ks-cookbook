# Sales: Realtime Voice SDR


**Tags:** `sales` `sdr` `realtime-api` `voice` `mcp` `function-calling`

A live SDR agent running on the OpenAI Realtime API with every KS MCP
tool exposed as a function call. Defaults to a typed REPL over the
Realtime websocket (useful for CI + smoke tests). Flip `--voice` and
install the `[voice]` extras to use your mic + speakers instead.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to
create that folder and upload the expected documents **before** running,
otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** product one-pager, ICP, past-wins library, objection
library, pricing. (Same corpus shape as
[`conversational_sdr_bot`](../conversational_sdr_bot/).)

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `SALES_CORPUS_FOLDER_ID=<your-folder-id> make demo-voice-sdr`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

## Run

Text mode (default — no audio hardware needed):

```bash
make demo-voice-sdr   # defaults: PROSPECT="Paloma Networks"
```

Voice mode (needs mic + speakers):

```bash
uv pip install 'ks-cookbook-voice-sdr[voice]'
uv run --package ks-cookbook-voice-sdr ks-cookbook-voice-sdr \
    --prospect "Paloma Networks" --voice
```

Output: `sample_output.md` — MEDDIC scorecard, discovered pains, open
objections, tool-call count, and a concrete next step.

## How it works

1. At startup we open an MCP stdio session to `ks-mcp` and call
   `session.list_tools()` to discover every tool in the KS surface.
2. Each MCP tool is re-encoded as an OpenAI Realtime API function-tool
   schema and sent in the `session.update` event. The Realtime model can
   then call KS tools mid-conversation.
3. Incoming `response.function_call_arguments.done` events are proxied to
   the MCP client; the result is posted back as a
   `conversation.item.create` of type `function_call_output`.
4. On session end a separate pydantic-ai summarizer reruns over the
   transcript to produce a strict `SessionSummary` (no optimism bias).

**Text mode** round-trips text deltas (`response.text.delta`) and exercises
the full tool-proxy path without needing any audio dependencies. **Voice
mode** uses `sounddevice` for 24 kHz mono PCM16 capture + playback and
relies on the server's VAD to commit turns.

## Framework

- **OpenAI Realtime API** (`gpt-4o-realtime-preview`) for the live session.
- **mcp** stdio client for the KS tool proxy.
- **pydantic-ai** for the MEDDIC-scored summary pass.

## Related

- `flagships/conversational_sdr_bot/` — the text-only, pydantic-ai-native
  version (no Realtime dependency).
- Recipes: `meddic_call_coach`, `outbound_call_prep`.
