# Default RFI input

Passed as CLI args to `make demo-rfi-agent`:

- `RFI_NUMBER="RFI-0147"`
- `QUESTION="Mechanical sheet M-402 calls for VAV box Greenheck SQ-120-B at
  grid line C.4 but spec 23 36 00 lists Price SDV-120 as basis of design.
  Confirm acceptable substitution or provide direction."`

A typical HVAC submittal clarification: spec vs drawing conflict with
possible substitution implications. The corpus (see `../README.md`)
contains the project specs, mechanical drawings, the HVAC submittal
register, and ASHRAE 62.1-2019.

## Use with your own RFI

```bash
RFI_NUMBER="RFI-0200" QUESTION="..." make demo-rfi-agent
```
