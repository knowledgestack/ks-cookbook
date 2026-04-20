# Default prospect input

Passed as CLI args to `make demo-voice-sdr`:

- `PROSPECT="Paloma Networks"`
- `PROSPECT_CONTEXT="VP Eng at a 400-person SaaS; inbound from a webinar."`

The agent connects to the OpenAI Realtime API, exposes KS MCP tools as
function calls, and runs either a typed REPL (default) or a voice session
(`--voice`). At session end it writes a MEDDIC-scored summary artifact.

## Use your own prospect

```bash
PROSPECT="Acme Co" PROSPECT_CONTEXT="..." make demo-voice-sdr
# voice mode (needs [voice] extras):
uv run --package ks-cookbook-voice-sdr ks-cookbook-voice-sdr \
    --prospect "Acme Co" --voice
```
