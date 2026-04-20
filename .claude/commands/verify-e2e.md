---
description: Run the full end-to-end verifier across every recipe + flagship, then have the cookbook-junior-dev agent triage the report. Accepts optional args like "--flagships-only", "--only icd10_coder,credit_memo_drafter", "--no-verify", "--limit 5".
argument-hint: [e2e_verify.py args, optional]
allowed-tools: Agent, Bash, Read, Grep
---

You are orchestrating an end-to-end verification of ks-cookbook. Your job
is to (1) run the verifier, (2) delegate triage of the report to the
cookbook-junior-dev agent, and (3) surface a short, actionable summary to
the user.

## Step 1 — Preflight

Run these checks in parallel:

```bash
make check-env
```

```bash
test -f scripts/e2e_verify.py && test -f scripts/e2e_recipe_inputs.json
```

If `check-env` fails (missing `KS_API_KEY` or LLM key), stop and tell the
user which key to set. If either script is missing, stop and tell the user
to `git pull`.

## Step 2 — Run the verifier

Invoke the e2e runner. Forward any arguments the user passed to this
command; otherwise run the full suite.

```bash
uv run python scripts/e2e_verify.py $ARGUMENTS 2>&1 | tee /tmp/ks-cookbook-e2e.log
```

The script:
- Runs every flagship via `make demo-<slug>` and every recipe with default
  args from `scripts/e2e_recipe_inputs.json`.
- Parses `[chunk:<uuid>]` markers from each output.
- Opens a KS MCP session and calls `read(path_part_id=<chunk>)` on every
  claimed chunk_id; flags fabricated / mismatched ones.
- Writes `e2e-report.json` at repo root.

Per-case verdicts you'll see:
`PASS | EMPTY_OUTPUT | MISSING_CITATIONS | FABRICATED_CHUNKS |
SNIPPET_MISMATCH | SCHEMA_ERROR | TIMEOUT | NEEDS_INPUTS | SKIPPED`

Note the run takes **real wall time** — the full 141-case suite with
citation verification is ~30–90 minutes depending on tenant latency and
model choice. If the user didn't pass `--limit` and the run will be long,
tell them before you start.

## Step 3 — Delegate triage

Spawn the `cookbook-junior-dev` agent with this exact prompt:

> You are triaging an e2e verification run of ks-cookbook. The full verdict
> report is at `e2e-report.json` (an array of result objects — each has
> `kind`, `name`, `verdict`, `seconds`, `stdout_tail`, `stderr_tail`,
> `artifact`, `citations_found`, `chunks_resolved`, `chunks_fabricated`,
> `snippet_mismatches`).
>
> Your job:
> 1. Read `e2e-report.json`. Summarize the pass/fail counts by verdict.
> 2. For every **non-SKIPPED, non-PASS, non-NEEDS_INPUTS** case, diagnose:
>    - `SCHEMA_ERROR` → grep the recipe/flagship source for the field that
>      failed validation; was it a required field with `min_length=1` that
>      the LLM returned empty? Is `*_FOLDER_ID` pointing at an empty folder?
>    - `EMPTY_OUTPUT` → retrieval returned zero citations. Almost always
>      means the configured corpus folder has no matching documents for
>      the recipe's domain. Tell the user which `*_FOLDER_ID` env var
>      governs this case (grep the recipe for `os.environ.get`).
>    - `FABRICATED_CHUNKS` → the LLM invented chunk UUIDs. This is a
>      prompt-hardening bug. Name the recipe/flagship and quote the
>      offending `chunk_id`s.
>    - `SNIPPET_MISMATCH` → chunk exists but the paraphrased snippet isn't
>      a substring of its body. Usually a prompt issue where the LLM is
>      paraphrasing rather than copying. Less severe than FABRICATED.
>    - `TIMEOUT` → note the recipe/flagship and suggest bumping
>      `--timeout` or picking a smaller model.
> 3. Produce a `docs/e2e-report.md` artifact with:
>    - Pass/fail totals.
>    - The triage findings grouped by category.
>    - A prioritized fix list (FABRICATED_CHUNKS > SCHEMA_ERROR > others).
>    - For each `NEEDS_INPUTS` recipe, the exact one-line JSON to add to
>      `scripts/e2e_recipe_inputs.json` (look at the recipe's argparse
>      required args and propose a sane default).
> 4. Do NOT attempt any fixes yourself. Your output is a report. The user
>    will decide what to fix.
>
> End your reply with: the path of the report you wrote and a one-line TL;DR
> like "3 FABRICATED_CHUNKS, 2 SCHEMA_ERROR, rest PASS — see docs/e2e-report.md".

## Step 4 — Return to user

Print the agent's TL;DR. Then give the user the three most useful next commands:

```bash
# Re-run a specific failure:
make e2e-one NAME=<failing_name>

# Re-run with verbose transcript:
uv run python scripts/e2e_verify.py --only <failing_name> --no-verify

# Inspect the full report:
cat docs/e2e-report.md
```

Do not summarize the entire report yourself — the agent already produced
`docs/e2e-report.md`. Your final message is ≤5 lines.

## Notes on cost + caching

- The full run calls the LLM once per case (~141 calls), plus MCP tool
  calls within each. Budget accordingly.
- `--no-verify` skips the citation-resolution step (no extra MCP reads),
  which cuts runtime roughly in half at the cost of missing
  `FABRICATED_CHUNKS` / `SNIPPET_MISMATCH` signals.
- `--limit 5` is the cheapest way to sanity-check the pipeline is wired
  correctly before a full run.
