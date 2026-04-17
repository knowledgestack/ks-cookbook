# Lease abstract generator


**Tags:** `real-estate` `leases` `commercial`

Read a commercial lease out of your KS tenant and emit a **one-page lease
abstract** (tenant, term, rent schedule, renewals, CAM, exclusives, radius
restriction) with citations to the clauses that ground each field.

This is the **VTS / Prophia / Lease Probe** asset-management use case —
instead of an analyst manually copying fields from a PDF, the agent reads the
lease and fills in the abstract template.

## Seed data required

This demo reads from a folder in your Knowledge Stack tenant. You need to create that folder and upload the expected documents **before** running, otherwise retrieval returns nothing and the demo fails with empty output.

**Expected corpus:** Retail and/or office lease samples.

Set-up steps:

1. Sign up at [app.knowledgestack.ai](https://app.knowledgestack.ai).
2. Create a folder in the dashboard and copy its folder ID.
3. Upload the documents described above into that folder.
4. Issue an API key from the dashboard and put it in `.env` as `KS_API_KEY`.
5. Run: `CORPUS_FOLDER_ID=<your-folder-id> make demo-lease-abstract`

Full corpus matrix for every flagship: [`docs/wiki/seed-data.md`](../../docs/wiki/seed-data.md).

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
