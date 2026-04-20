# Default well input

Passed as CLI args to `make demo-well-log`:

- `WELL_ID="42-255-31234"` (Texas RRC API number)

A hypothetical Permian Basin horizontal well. The corpus (see
`../README.md`) contains operator daily drilling reports, mudlogs, a state
RRC completion filing, and one SPE paper on the Wolfcamp formation.

## Use with your own well

```bash
WELL_ID="42-135-40999" make demo-well-log
```
