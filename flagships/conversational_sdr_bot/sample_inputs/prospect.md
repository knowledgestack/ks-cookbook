# Default prospect input

Passed as CLI args to `make demo-sdr-bot`:

- `PROSPECT="Paloma Networks"`
- `PROSPECT_CONTEXT="VP Eng at 400-person SaaS; inbound from a webinar; stack is Postgres + Snowflake."`

The bot runs as an interactive REPL — you play the prospect. Type `/end`
when done; a MEDDIC-scored transcript artifact is written to
`sample_output.md`.

## Use with your own prospect

```bash
PROSPECT="Acme Co" PROSPECT_CONTEXT="..." make demo-sdr-bot
```
