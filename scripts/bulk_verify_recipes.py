"""Run every recipe.py against the live KS tenant and capture pass/fail.

For each recipe directory, this script:
  1. Inspects the argparse signature (parses recipe.py with Python's ast)
     to discover required CLI args.
  2. Builds a reasonable default invocation — using sample_inputs/ files
     when present, plus a curated default for common arg names (--question,
     --contract, --company, --case-id, etc.).
  3. Runs the recipe with a 6-minute timeout, captures stdout, validates
     the result is JSON.
  4. Writes results to e2e_recipes_report.json with status (pass|skip|fail|
     timeout) plus the first 240 chars of the output.

Required env vars (read from process):
    KS_API_KEY, KS_BASE_URL, KS_MCP_COMMAND, OPENAI_API_KEY, MODEL.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RECIPES = REPO / "recipes"

# Reasonable defaults per common arg name. Keys are arg names without the --.
DEFAULTS: dict[str, str] = {
    "question": "What ERISA disclosures must an employer provide to participants in the SPD?",
    "contract": "Apple 2024 proxy",
    "case-id": "structuring-cash-deposits",
    "case_id": "structuring-cash-deposits",
    "company": "FreshFinTech",
    "blurb": "Series B B2B fintech, 250 employees, US + UK.",
    "party": "Jackson Women's Health Organization",
    "period": "Q1 2026",
    "endpoint": "POST /v1/ingest",
    "replacement": "POST /v2/ingest",
    "sunset": "2026-12-31",
    "version": "v2.4.0",
    "date": "2026-04-27",
    "note": "Patient with NSTEMI, T2DM with neuropathy, HTN.",
    "description": "Client dinner at Smith & Wollensky NYC",
    "amount": "$485.00",
    "category": "entertainment",
    "type": "erasure",
    "jurisdiction": "GDPR",
    "subject": "former EU customer, marketing preferences + transaction history",
    "name": "Acme Corp",
    "asset-class": "corporate",
    "asset_class": "corporate",
    "counterparty": "BB-rated corporate",
    "notional": "10000000",
    "tenant-id": "tenant-1",
    "tenant_id": "tenant-1",
    "ticker": "KO",
    "url": "https://example.com",
    "title": "Q4 board update",
    "topic": "Q4 board update",
    "audience": "engineering team",
    "industry": "fintech",
    "claim-id": "CL-2025-0142",
    "claim_id": "CL-2025-0142",
    "incident-id": "INC-2025-0042",
    "incident_id": "INC-2025-0042",
    "policy-id": "POL-2025-0142",
    "policy_id": "POL-2025-0142",
    "lead-id": "LEAD-2025-0042",
    "lead_id": "LEAD-2025-0042",
    "ticket-id": "TKT-2025-0042",
    "ticket_id": "TKT-2025-0042",
    "id": "ID-2025-0042",
    "user": "user@example.com",
    "user-id": "U-2025-0042",
    "user_id": "U-2025-0042",
    "deal-id": "DEAL-2025-0042",
    "deal_id": "DEAL-2025-0042",
    "team": "platform",
    "doc-id": "019dd1f7-65c9-74db-aa97-39e4447fbbd1",
    "doc_id": "019dd1f7-65c9-74db-aa97-39e4447fbbd1",
    "save": "",
    "service": "ingest-api",
    "capacity-days": "10",
    "capacity_days": "10",
    "scenario": "baseline",
    "sprint": "FY26-Q2-S1",
    "pr": "PR-1234",
    "risk": "high",
    "vendor": "Acme Vendor LLC",
    "drug": "metformin",
    "event": "Patient developed lactic acidosis on day 7 of metformin therapy.",
}


def parse_argparse(recipe: Path) -> list[tuple[str, dict]]:
    """Extract argparse arguments via AST. Returns [(flag, attrs), ...]."""
    tree = ast.parse(recipe.read_text())
    args: list[tuple[str, dict]] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "add_argument"):
            continue
        if not node.args:
            continue
        first = node.args[0]
        if not isinstance(first, ast.Constant) or not isinstance(first.value, str):
            continue
        flag = first.value
        attrs: dict = {}
        for kw in node.keywords:
            if isinstance(kw.value, ast.Constant):
                attrs[kw.arg] = kw.value.value
        args.append((flag, attrs))
    return args


def build_cmdline(recipe: Path) -> list[str] | None:
    """Construct a recipe invocation. Return None if we can't build defaults."""
    cmd: list[str] = ["uv", "run", "python", str(recipe.relative_to(REPO))]
    sample_dir = recipe.parent / "sample_inputs"
    sample_files = sorted(p for p in sample_dir.iterdir()) if sample_dir.is_dir() else []

    for flag, attrs in parse_argparse(recipe):
        if not flag.startswith("--"):
            continue
        name = flag[2:]
        # Skip store_true/store_false flags entirely.
        if attrs.get("action") in ("store_true", "store_false"):
            continue
        # If a default is set, skip — argparse will use it.
        if attrs.get("required") is not True and "default" in attrs:
            continue
        # File-typed args: pull from sample_inputs/.
        is_file_arg = (
            name.endswith("-file") or name.endswith("_file")
            or name in ("csv", "cur-file", "cur_file", "note-file", "note_file",
                        "commits-file", "commits_file", "input", "doc", "template")
        )
        if is_file_arg and sample_files:
            cmd += [flag, str(sample_files[0].relative_to(REPO))]
            continue
        if is_file_arg and not sample_files:
            return None  # Can't satisfy a required file arg without samples.
        # String defaults.
        val = DEFAULTS.get(name, DEFAULTS.get(name.replace("-", "_")))
        if val is None:
            # Ultimate fallback for any required string arg.
            val = "demo"
        cmd += [flag, val]
    return cmd


def run_one(recipe: Path, timeout_s: int = 360) -> dict:
    rec = recipe.parent.name
    cmd = build_cmdline(recipe)
    if cmd is None:
        return {"recipe": rec, "status": "skip",
                "reason": "required file arg with no sample_inputs"}
    started = time.monotonic()
    try:
        r = subprocess.run(
            cmd, cwd=REPO, timeout=timeout_s,
            capture_output=True, text=True, env=os.environ.copy(),
        )
    except subprocess.TimeoutExpired:
        return {"recipe": rec, "status": "timeout",
                "cmd": " ".join(shlex.quote(c) for c in cmd),
                "elapsed_s": round(time.monotonic() - started, 1)}
    elapsed = round(time.monotonic() - started, 1)
    out = (r.stdout or "").strip()
    err_tail = (r.stderr or "").strip().splitlines()[-3:]
    if r.returncode != 0:
        return {"recipe": rec, "status": "fail",
                "cmd": " ".join(shlex.quote(c) for c in cmd),
                "exit_code": r.returncode, "elapsed_s": elapsed,
                "stderr_tail": err_tail}
    # Validate output is JSON.
    try:
        json.loads(out)
    except json.JSONDecodeError:
        return {"recipe": rec, "status": "fail",
                "reason": "stdout not JSON",
                "cmd": " ".join(shlex.quote(c) for c in cmd),
                "stdout_head": out[:240], "elapsed_s": elapsed}
    return {"recipe": rec, "status": "pass", "elapsed_s": elapsed,
            "output_size": len(out),
            "stdout_head": out[:240]}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--limit", type=int, default=0, help="Run at most N recipes (0=all).")
    p.add_argument("--start", default="",
                   help="Skip recipes alphabetically before this name.")
    p.add_argument("--only", default="",
                   help="Comma-separated recipe names; run only these.")
    p.add_argument("--out", default=str(REPO / "e2e_recipes_report.json"))
    p.add_argument("--timeout", type=int, default=360)
    args = p.parse_args()

    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY before running.")

    only = set(filter(None, args.only.split(","))) if args.only else None
    targets = sorted(d for d in RECIPES.iterdir()
                     if d.is_dir() and not d.name.startswith("_") and (d / "recipe.py").exists())
    if only:
        targets = [d for d in targets if d.name in only]
    if args.start:
        targets = [d for d in targets if d.name >= args.start]
    if args.limit:
        targets = targets[: args.limit]

    print(f"# running {len(targets)} recipe(s)", file=sys.stderr)
    results: list[dict] = []
    for d in targets:
        rp = d / "recipe.py"
        print(f"  → {d.name} ...", file=sys.stderr, flush=True)
        res = run_one(rp, timeout_s=args.timeout)
        results.append(res)
        print(f"     {res['status']} ({res.get('elapsed_s', 0)}s)", file=sys.stderr)
        # Stream the report to disk after each run so partial results survive.
        Path(args.out).write_text(json.dumps(
            {"results": results,
             "summary": {s: sum(1 for r in results if r["status"] == s)
                         for s in ("pass", "fail", "skip", "timeout")}},
            indent=2,
        ))

    summary = {s: sum(1 for r in results if r["status"] == s)
               for s in ("pass", "fail", "skip", "timeout")}
    print(f"\n# summary: {summary}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
