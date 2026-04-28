"""Smoke-test every recipe by running ``python recipe.py --help``.

This catches the testable-without-a-tenant failures:
  - broken imports
  - argparse misconfigurations
  - pydantic schema build errors
  - shared module breakage

What it CANNOT verify without a live KS tenant + MCP + LLM key:
  - actual MCP tool calls
  - corpus retrieval
  - citation grounding
  - LLM output structure

Exit 0 iff every recipe's --help succeeds. Prints a per-recipe pass/fail table.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECIPES = ROOT / "recipes"
FLAGSHIPS = ROOT / "flagships"

# Recipes that intentionally short-circuit on import (env-var guards before
# argparse) — smoke-test has no meaningful signal for them.
KNOWN_SKIPS: set[str] = {"permission_aware_retrieval"}


def _recipe_targets() -> list[Path]:
    out: list[Path] = []
    for child in sorted(RECIPES.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        if child.name in KNOWN_SKIPS:
            continue
        entry = child / "recipe.py"
        if entry.exists():
            out.append(entry)
    return out


def _flagship_targets() -> list[tuple[str, str]]:
    """Flagships expose a [project.scripts] entrypoint ``ks-cookbook-<slug>``.

    We parse each package's pyproject for the script name rather than guessing.
    """
    out: list[tuple[str, str]] = []
    for child in sorted(FLAGSHIPS.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        pyproj = child / "pyproject.toml"
        if not pyproj.exists():
            continue
        script = None
        pkg = None
        for line in pyproj.read_text().splitlines():
            line = line.strip()
            if line.startswith("name = ") and pkg is None:
                pkg = line.split("=", 1)[1].strip().strip('"')
            if line.startswith("ks-cookbook-") and "=" in line and script is None:
                script = line.split("=", 1)[0].strip()
        if pkg and script:
            out.append((pkg, script))
    return out


def _run_help(cmd: list[str]) -> tuple[bool, str]:
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=45,
            cwd=ROOT,
            env={**os.environ, "KS_API_KEY": "smoke"},
        )
    except subprocess.TimeoutExpired:
        return False, "timeout"
    ok = r.returncode == 0
    tail = (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]
    return ok, tail[0][:180]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--recipes-only", action="store_true")
    p.add_argument("--flagships-only", action="store_true")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    failures: list[tuple[str, str]] = []
    passed = 0

    if not args.flagships_only:
        for entry in _recipe_targets():
            name = entry.parent.name
            ok, tail = _run_help(["uv", "run", "python", str(entry), "--help"])
            if args.verbose or not ok:
                print(f"{'PASS' if ok else 'FAIL'}  recipe  {name:40s}  {tail if not ok else ''}")
            if ok:
                passed += 1
            else:
                failures.append((f"recipe:{name}", tail))

    if not args.recipes_only:
        for pkg, script in _flagship_targets():
            name = pkg.replace("ks-cookbook-", "")
            ok, tail = _run_help(["uv", "run", "--package", pkg, script, "--help"])
            if args.verbose or not ok:
                print(f"{'PASS' if ok else 'FAIL'}  flag    {name:40s}  {tail if not ok else ''}")
            if ok:
                passed += 1
            else:
                failures.append((f"flagship:{name}", tail))

    total = passed + len(failures)
    print(
        f"\nSmoke test: {passed}/{total} passed, {len(failures)} failed, "
        f"{len(KNOWN_SKIPS)} skipped (env-guarded)."
    )
    for label, tail in failures:
        print(f"  FAIL {label}: {tail}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
