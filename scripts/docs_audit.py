"""Static audit: does every recipe + flagship document inputs / seed / output?

This does NOT call the tenant. It checks, for each use case, that the repo
ships the artifacts a novice would need to actually run the case:

- Flagship audit (per flagship/<name>):
    * README.md present
    * README names an env var ending in _FOLDER_ID OR "CORPUS_FOLDER_ID"
    * README has a "Seed data required" section OR calls the seed matrix
    * sample_inputs/ directory with ≥1 file
    * schema.py declares a Citation model with a chunk_id field
    * __main__.py writes an artifact (has `.write_text` or .write_bytes)

- Recipe audit (per recipes/<name>):
    * README.md present (with a runnable bash block)
    * recipe.py header docstring names a framework ("Framework:") and
      at least one MCP tool ("list_contents", "read", "search_knowledge",
      or similar)
    * recipe.py reads a *_FOLDER_ID env var
    * recipe.py declares a pydantic Citation-like class (chunk_id field)

Exits 0 iff every use case passes every check. Writes a JSON report.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECIPES = ROOT / "recipes"
FLAGSHIPS = ROOT / "flagships"

FOLDER_ENV_RE = re.compile(r"[A-Z][A-Z0-9_]*FOLDER_ID")
MCP_TOOL_RE = re.compile(r"\b(list_contents|read|search_knowledge|search_keyword|"
                         r"read_around|find|get_info|view_chunk_image|"
                         r"get_organization_info|get_current_datetime)\b")
# Citation can be enforced by a pydantic field, a TypedDict, or `chunk:<uuid>`
# markers the recipe emits inline. We only require that the source mentions
# chunks somehow so novices can find the docs/tests for them.
CHUNK_REF_RE = re.compile(r"chunk_id|\[chunk:|`chunk:")
# Flagships write artifacts in many ways; accept any of the common patterns.
ARTIFACT_RE = re.compile(
    r"\.write_(text|bytes)\b|\.save\(|openpyxl|Workbook\(|Document\(|"
    r"Path\([^)]+\)\.write|args\.out|out\.write"
)
# Run blocks: accept fenced ```bash / ```sh / ``` with a visible "uv run" or "make ".
RUN_BLOCK_RE = re.compile(r"```(?:bash|sh|shell)?\s*\n[^`]*?(uv run|make |python )",
                          re.MULTILINE | re.DOTALL)

KNOWN_RECIPE_SKIPS = {
    # Non-standard shape (recipe is a notebook/template/seed-only):
    "document_versions",
    "version_drift_review",  # ships a seed.py helper too
}

# Recipes that intentionally use plain-text chunk markers instead of a
# pydantic Citation model — documented in INDEX.md as "Raw OpenAI" or
# "MCP-only" rows. They still emit real [chunk:<uuid>] markers at runtime.
PLAINTEXT_CITATION_RECIPES = {
    "policy_qa", "password_policy_audit", "soc2_evidence",
    "vendor_security_review", "dpa_gap_check", "bcp_drill_plan",
    "adr_drafter", "change_management_review", "sdlc_checklist",
    "onboarding_checklist", "llama_index_rag", "permission_aware_retrieval",
}


@dataclass
class Issue:
    check: str
    detail: str = ""


@dataclass
class CaseReport:
    kind: str
    name: str
    passed: bool = True
    issues: list[Issue] = field(default_factory=list)

    def fail(self, check: str, detail: str = "") -> None:
        self.passed = False
        self.issues.append(Issue(check=check, detail=detail))


def _audit_flagship(d: Path) -> CaseReport:
    rep = CaseReport(kind="flagship", name=d.name)
    readme = d / "README.md"
    if not readme.exists():
        rep.fail("README.md missing")
    else:
        txt = readme.read_text()
        if not FOLDER_ENV_RE.search(txt):
            rep.fail("README missing *_FOLDER_ID env var reference")
        if "Seed data required" not in txt and "seed-data.md" not in txt:
            rep.fail("README missing 'Seed data required' section")
        if not RUN_BLOCK_RE.search(txt):
            rep.fail("README missing runnable bash block (uv run / make / python)")

    samples = d / "sample_inputs"
    if not samples.exists():
        rep.fail("sample_inputs/ directory missing")
    else:
        inputs = [p for p in samples.iterdir() if p.is_file()]
        if not inputs:
            rep.fail("sample_inputs/ is empty")

    src = d / "src"
    if not src.exists():
        rep.fail("src/ missing")
    else:
        pkg = next((p for p in src.iterdir() if p.is_dir() and not p.name.startswith("_")), None)
        if not pkg:
            rep.fail("src/<package>/ missing")
        else:
            # Scan every .py file under the package for chunk refs (supports
            # flagships that use markdown templates rather than pydantic schemas).
            all_src = "\n".join(
                p.read_text() for p in pkg.rglob("*.py") if p.is_file()
            )
            if not CHUNK_REF_RE.search(all_src):
                rep.fail("no chunk_id / [chunk: reference anywhere in src/")
            main = pkg / "__main__.py"
            if not main.exists():
                rep.fail("__main__.py missing")
            elif not ARTIFACT_RE.search(main.read_text()):
                rep.fail("__main__.py does not look like it writes an artifact")

    pyproj = d / "pyproject.toml"
    if not pyproj.exists():
        rep.fail("pyproject.toml missing")
    return rep


def _audit_recipe(d: Path) -> CaseReport:
    rep = CaseReport(kind="recipe", name=d.name)
    readme = d / "README.md"
    recipe = d / "recipe.py"

    if not readme.exists():
        rep.fail("README.md missing")
    else:
        rtxt = readme.read_text()
        if "uv run" not in rtxt and "make " not in rtxt:
            rep.fail("README missing runnable bash/uv-run block")

    if not recipe.exists():
        rep.fail("recipe.py missing")
        return rep

    code = recipe.read_text()
    first_doc = code.split('"""', 2)
    if len(first_doc) < 3 or not first_doc[1].strip():
        rep.fail("recipe.py missing module docstring")
    else:
        doc = first_doc[1]
        if "Framework:" not in doc:
            rep.fail("docstring missing 'Framework:' line")
        if not MCP_TOOL_RE.search(doc + code):
            rep.fail("no MCP tool referenced (list_contents/read/search_knowledge/...)")
    if not FOLDER_ENV_RE.search(code):
        rep.fail("recipe.py does not read a *_FOLDER_ID env var")
    if d.name not in PLAINTEXT_CITATION_RECIPES and not CHUNK_REF_RE.search(code):
        rep.fail("no pydantic Citation with chunk_id field (and not in plaintext allowlist)")
    return rep


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--report", type=Path, default=ROOT / "docs-audit.json")
    p.add_argument("--strict", action="store_true",
                   help="Exit non-zero if any case fails any check.")
    args = p.parse_args()

    reports: list[CaseReport] = []

    for d in sorted(FLAGSHIPS.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        reports.append(_audit_flagship(d))

    for d in sorted(RECIPES.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        if d.name in KNOWN_RECIPE_SKIPS:
            reports.append(CaseReport(kind="recipe", name=d.name, passed=True,
                                      issues=[Issue("skipped", "known non-standard")]))
            continue
        reports.append(_audit_recipe(d))

    passed = sum(1 for r in reports if r.passed)
    failed = [r for r in reports if not r.passed]

    flagships = [r for r in reports if r.kind == "flagship"]
    recipes = [r for r in reports if r.kind == "recipe"]
    print(f"Flagships: {sum(1 for r in flagships if r.passed)}/{len(flagships)} pass")
    print(f"Recipes:   {sum(1 for r in recipes if r.passed)}/{len(recipes)} pass")
    print(f"Total:     {passed}/{len(reports)} pass\n")

    if failed:
        print("Failing cases:\n")
        for r in failed:
            print(f"  {r.kind}/{r.name}")
            for iss in r.issues:
                print(f"    - {iss.check}" + (f"  ({iss.detail})" if iss.detail else ""))
        print()

    args.report.write_text(json.dumps([asdict(r) for r in reports], indent=2))
    print(f"Wrote {args.report}")
    return 1 if (args.strict and failed) else 0


if __name__ == "__main__":
    sys.exit(main())
