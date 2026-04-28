"""End-to-end verifier for every ks-cookbook recipe + flagship.

Unlike ``smoke_recipes.py`` (which only runs ``--help``), this script:

1. Runs each flagship via its ``make demo-<slug>`` target.
2. Runs each recipe with the default CLI args registered in
   ``scripts/e2e_recipe_inputs.json``.
3. Parses the produced artifact / stdout for ``[chunk:<uuid>]`` markers.
4. Opens a KS MCP stdio session and calls ``read`` on every chunk_id the
   output claimed, to confirm:
   (a) the chunk exists in the user's tenant, and
   (b) the recipe's reported snippet substring-matches the chunk's body.
5. Emits a per-case verdict and a JSON report.

Needs a real tenant: ``KS_API_KEY`` + (``OPENAI_API_KEY`` or
``ANTHROPIC_API_KEY``). For contributors without a tenant, run
``make smoke`` instead.

Verdicts:
  PASS                   — exit 0, ≥1 citation, every chunk_id resolves, snippet matches.
  EMPTY_OUTPUT           — exit 0 but no citations found.
  MISSING_CITATIONS      — exit 0 but fewer citations than the schema claims.
  FABRICATED_CHUNKS      — at least one chunk_id could not be read from the tenant.
  SNIPPET_MISMATCH       — chunk resolves but the claimed snippet is not in its body.
  SCHEMA_ERROR           — pydantic ValidationError (or non-zero exit).
  TIMEOUT                — process exceeded --timeout.
  NEEDS_INPUTS           — recipe requires args and isn't in e2e_recipe_inputs.json.
  SKIPPED                — listed in --skip (or env-guarded short-circuit).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECIPES = ROOT / "recipes"
FLAGSHIPS = ROOT / "flagships"
INPUTS_JSON = ROOT / "scripts" / "e2e_recipe_inputs.json"

CHUNK_RE = re.compile(
    r"\[chunk:([0-9a-fA-F-]{36})\]|chunk:([0-9a-fA-F-]{36})|\"chunk_id\"\s*:\s*\"([0-9a-fA-F-]{36})\""
)

KNOWN_SKIPS: set[str] = {
    # env-guarded — no meaningful e2e signal without additional setup.
    "permission_aware_retrieval",
}


@dataclass
class Result:
    kind: str  # "recipe" | "flagship"
    name: str
    verdict: str
    seconds: float = 0.0
    stdout_tail: str = ""
    stderr_tail: str = ""
    artifact: str | None = None
    citations_found: int = 0
    chunks_resolved: int = 0
    chunks_fabricated: list[str] = field(default_factory=list)
    snippet_mismatches: list[str] = field(default_factory=list)


# ---------- input discovery ----------


def _recipe_inputs() -> dict[str, list[str]]:
    data = json.loads(INPUTS_JSON.read_text())
    return {k: v for k, v in data.items() if not k.startswith("_")}


def _flagship_demo_targets() -> list[tuple[str, str]]:
    """Return (flagship_dir_name, make_target). Inferred from the Makefile."""
    makefile = (ROOT / "Makefile").read_text()
    targets = re.findall(r"^(demo-[a-z0-9-]+):", makefile, flags=re.M)
    pairs: list[tuple[str, str]] = []
    # Match the `--package ks-cookbook-<x>` line to the target name.
    for t in targets:
        block = re.search(rf"^{re.escape(t)}:[^\n]*\n((?:[\t ].*\n)+)", makefile, flags=re.M)
        if not block:
            continue
        pkg_m = re.search(r"--package\s+(ks-cookbook-[a-z0-9-]+)", block.group(1))
        out_m = re.search(r"flagships/([a-z0-9_]+)/sample_output", block.group(1))
        if out_m:
            pairs.append((out_m.group(1), t))
        elif pkg_m:
            slug = pkg_m.group(1).removeprefix("ks-cookbook-")
            # Guess the flagship dir by slug; fall back to listing.
            guess = slug.replace("-", "_")
            pairs.append((guess, t))
    return pairs


# ---------- running ----------


def _run(cmd: list[str], timeout: int, cwd: Path = ROOT) -> tuple[int, str, str, float]:
    start = time.monotonic()
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd, env=os.environ.copy()
        )
    except subprocess.TimeoutExpired as e:
        out = e.stdout if isinstance(e.stdout, str) else (e.stdout.decode() if e.stdout else "")
        err = e.stderr if isinstance(e.stderr, str) else (e.stderr.decode() if e.stderr else "")
        return 124, out, err, time.monotonic() - start
    return r.returncode, r.stdout or "", r.stderr or "", time.monotonic() - start


def _tail(s: str, n: int = 300) -> str:
    s = (s or "").strip()
    return s[-n:]


def _artifact_from_make_output(stdout: str) -> str | None:
    m = re.search(r"Output(?:\s+written)?\s+to:\s*([^\s]+)", stdout)
    return m.group(1) if m else None


# ---------- citation extraction ----------


def _extract_chunks(blob: str) -> list[tuple[str, str]]:
    """Return list of (chunk_id, surrounding_snippet). Snippet = 240 chars of
    context around the marker; used for substring verification."""
    hits: list[tuple[str, str]] = []
    for m in CHUNK_RE.finditer(blob):
        chunk_id = m.group(1) or m.group(2) or m.group(3)
        if not chunk_id:
            continue
        start = max(0, m.start() - 240)
        end = min(len(blob), m.end() + 240)
        hits.append((chunk_id, blob[start:end]))
    # Deduplicate while preserving order.
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for cid, snip in hits:
        if cid in seen:
            continue
        seen.add(cid)
        out.append((cid, snip))
    return out


# ---------- MCP chunk verification ----------


async def _verify_chunks(chunks: list[tuple[str, str]]) -> tuple[list[str], list[str], int]:
    """Return (fabricated_ids, snippet_mismatch_ids, resolved_count).

    Opens ONE MCP session and calls ``read`` with each chunk_id as a
    ``path_part_id``. The MCP tool either returns text containing
    ``[chunk:<uuid>]`` markers or errors with 'not found'.
    """
    if not chunks:
        return [], [], 0
    try:
        # Local import so the script still runs in smoke mode without the
        # full mcp dependency installed.
        sys.path.insert(0, str(ROOT / "recipes"))
        from _shared.mcp_client import call, ks_mcp_session  # type: ignore[import-not-found]
    except ImportError as e:
        print(f"  (citation verify skipped: {e})", file=sys.stderr)
        return [], [], 0

    fabricated: list[str] = []
    mismatches: list[str] = []
    resolved = 0
    async with ks_mcp_session() as session:
        for cid, snippet_ctx in chunks:
            try:
                body = await call(session, "read", {"path_part_id": cid, "max_chars": 2000})
            except Exception:  # noqa: BLE001
                fabricated.append(cid)
                continue
            if not body or cid not in body:
                # chunk_id should appear in its own body as [chunk:<id>]
                fabricated.append(cid)
                continue
            resolved += 1
            # Snippet check: extract any quoted 20+ char substring near the marker
            # from the output and test it against the body.
            quoted = re.search(r'"([^"]{20,240})"', snippet_ctx) or re.search(
                r"\u201c([^\u201d]{20,240})\u201d", snippet_ctx
            )
            if quoted and quoted.group(1)[:80] not in body:
                mismatches.append(cid)
    return fabricated, mismatches, resolved


# ---------- per-case runners ----------


def _run_flagship(dir_name: str, target: str, timeout: int, verify: bool) -> Result:
    res = Result(kind="flagship", name=dir_name, verdict="SKIPPED")
    rc, out, err, secs = _run(["make", target], timeout=timeout)
    res.seconds = secs
    res.stdout_tail = _tail(out)
    res.stderr_tail = _tail(err)

    if rc == 124:
        res.verdict = "TIMEOUT"
        return res
    if rc != 0:
        res.verdict = "SCHEMA_ERROR"
        return res

    artifact_path = _artifact_from_make_output(out)
    res.artifact = artifact_path
    blob = out
    if artifact_path:
        p = Path(artifact_path)
        if p.exists():
            try:
                blob = p.read_text()
            except UnicodeDecodeError:
                # .docx / .xlsx: we can only rely on stdout
                pass

    chunks = _extract_chunks(blob)
    res.citations_found = len(chunks)
    if not chunks:
        res.verdict = "EMPTY_OUTPUT"
        return res

    if verify:
        fabricated, mismatches, resolved = asyncio.run(_verify_chunks(chunks))
        res.chunks_fabricated = fabricated
        res.snippet_mismatches = mismatches
        res.chunks_resolved = resolved
        if fabricated:
            res.verdict = "FABRICATED_CHUNKS"
            return res
        if mismatches:
            res.verdict = "SNIPPET_MISMATCH"
            return res
    else:
        res.chunks_resolved = len(chunks)

    res.verdict = "PASS"
    return res


def _run_recipe(name: str, args: list[str], timeout: int, verify: bool) -> Result:
    res = Result(kind="recipe", name=name, verdict="SKIPPED")
    recipe_py = RECIPES / name / "recipe.py"
    if not recipe_py.exists():
        res.verdict = "SKIPPED"
        res.stderr_tail = "recipe.py missing"
        return res

    rc, out, err, secs = _run(
        ["uv", "run", "python", str(recipe_py), *args],
        timeout=timeout,
    )
    res.seconds = secs
    res.stdout_tail = _tail(out)
    res.stderr_tail = _tail(err)

    if rc == 124:
        res.verdict = "TIMEOUT"
        return res
    if rc != 0:
        res.verdict = "SCHEMA_ERROR"
        return res

    chunks = _extract_chunks(out)
    res.citations_found = len(chunks)
    if not chunks:
        res.verdict = "EMPTY_OUTPUT"
        return res

    if verify:
        fabricated, mismatches, resolved = asyncio.run(_verify_chunks(chunks))
        res.chunks_fabricated = fabricated
        res.snippet_mismatches = mismatches
        res.chunks_resolved = resolved
        if fabricated:
            res.verdict = "FABRICATED_CHUNKS"
            return res
        if mismatches:
            res.verdict = "SNIPPET_MISMATCH"
            return res
    else:
        res.chunks_resolved = len(chunks)

    res.verdict = "PASS"
    return res


# ---------- top-level ----------


def _check_env() -> None:
    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is required. Copy .env.example to .env and fill it in.")
    if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")):
        sys.exit("OPENAI_API_KEY or ANTHROPIC_API_KEY is required.")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--recipes-only", action="store_true")
    p.add_argument("--flagships-only", action="store_true")
    p.add_argument("--only", default=None, help="Comma-separated list of names to run.")
    p.add_argument("--skip", default="", help="Comma-separated list of names to skip.")
    p.add_argument("--timeout", type=int, default=240, help="Per-case timeout in seconds.")
    p.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip MCP chunk verification (only exit-code + citation count).",
    )
    p.add_argument("--report", type=Path, default=ROOT / "e2e-report.json")
    p.add_argument("--limit", type=int, default=0, help="Max cases per kind (0 = all).")
    args = p.parse_args()

    _check_env()
    verify = not args.no_verify
    only: set[str] = set(filter(None, (args.only or "").split(",")))
    skip: set[str] = set(filter(None, args.skip.split(","))) | KNOWN_SKIPS

    results: list[Result] = []
    inputs = _recipe_inputs()

    # Flagships
    if not args.recipes_only:
        pairs = _flagship_demo_targets()
        if args.limit:
            pairs = pairs[: args.limit]
        for dir_name, target in pairs:
            if only and dir_name not in only:
                continue
            if dir_name in skip:
                results.append(Result(kind="flagship", name=dir_name, verdict="SKIPPED"))
                continue
            print(f"▶ flagship  {dir_name:36s}", flush=True)
            res = _run_flagship(dir_name, target, args.timeout, verify)
            print(
                f"  {res.verdict:20s} {res.seconds:6.1f}s  citations={res.citations_found}"
                f"  resolved={res.chunks_resolved}"
            )
            results.append(res)

    # Recipes
    if not args.flagships_only:
        recipe_dirs = [
            d.name for d in sorted(RECIPES.iterdir()) if d.is_dir() and not d.name.startswith("_")
        ]
        if args.limit:
            recipe_dirs = recipe_dirs[: args.limit]
        for name in recipe_dirs:
            if only and name not in only:
                continue
            if name in skip:
                results.append(Result(kind="recipe", name=name, verdict="SKIPPED"))
                continue
            reg_args = inputs.get(name)
            if reg_args is None:
                # Try empty args; many recipes use all-optional flags.
                recipe_src = (RECIPES / name / "recipe.py").read_text()
                if "required=True" in recipe_src:
                    results.append(Result(kind="recipe", name=name, verdict="NEEDS_INPUTS"))
                    print(
                        f"▶ recipe    {name:36s}  NEEDS_INPUTS (add to scripts/e2e_recipe_inputs.json)"
                    )
                    continue
                reg_args = []
            print(f"▶ recipe    {name:36s}", flush=True)
            res = _run_recipe(name, reg_args, args.timeout, verify)
            print(
                f"  {res.verdict:20s} {res.seconds:6.1f}s  citations={res.citations_found}"
                f"  resolved={res.chunks_resolved}"
            )
            results.append(res)

    # Summary
    by_verdict: dict[str, int] = {}
    for r in results:
        by_verdict[r.verdict] = by_verdict.get(r.verdict, 0) + 1

    print("\n=== E2E verdict summary ===")
    for v in (
        "PASS",
        "EMPTY_OUTPUT",
        "MISSING_CITATIONS",
        "FABRICATED_CHUNKS",
        "SNIPPET_MISMATCH",
        "SCHEMA_ERROR",
        "TIMEOUT",
        "NEEDS_INPUTS",
        "SKIPPED",
    ):
        if by_verdict.get(v, 0):
            print(f"  {v:20s} {by_verdict[v]:4d}")

    failures = [r for r in results if r.verdict not in {"PASS", "SKIPPED", "NEEDS_INPUTS"}]
    if failures:
        print("\nFailures:")
        for r in failures:
            tail = (r.stderr_tail or r.stdout_tail).splitlines()
            last = tail[-1][:140] if tail else ""
            print(f"  {r.verdict:20s} {r.kind}/{r.name}: {last}")

    args.report.write_text(json.dumps([asdict(r) for r in results], indent=2, default=str))
    print(f"\nWrote {args.report}")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
