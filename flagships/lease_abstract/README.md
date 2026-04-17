# Lease abstract generator

Read a commercial lease out of your KS tenant and emit a **one-page lease
abstract** (tenant, term, rent schedule, renewals, CAM, exclusives, radius
restriction) with citations to the clauses that ground each field.

This is the **VTS / Prophia / Lease Probe** asset-management use case —
instead of an analyst manually copying fields from a PDF, the agent reads the
lease and fills in the abstract template.

## Run

```bash
make demo-lease-abstract-setup   # seeds the sample retail + office leases
export CORPUS_FOLDER_ID="<printed by setup>"
make demo-lease-abstract         # LEASE=retail_lease_pinetree_crossing by default
```

Output: `lease-abstract.md` — a one-page markdown abstract with inline
`[chunk:<uuid>]` citations next to each field.

## Framework

**Raw OpenAI function calling** — no LangChain, no pydantic-ai. Shows the
minimum possible plumbing to wire an agent to the KS HTTP API through two
thin tool wrappers (`list_contents`, `read`). Everything else is a hand-rolled
`while tool_calls:` loop over `client.chat.completions.create`.

## What the agent does

1. Calls `list_contents(corpus_folder)` to see the leases and the template.
2. Calls `read(<template>)` to internalize the required abstract fields.
3. Calls `read(<target lease>)` and iterates via `read_around` if needed.
4. Emits plain markdown following the abstract template, citing each field
   with the chunk IDs it pulled from the `read` output.
