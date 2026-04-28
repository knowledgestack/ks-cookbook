"""Bulk refactor cookbook recipes to the verified architecture.

For each recipe.py:
  1. Strip the CORPUS = os.environ.get("X_FOLDER_ID", ...) line (recipes
     no longer hard-code folder UUIDs).
  2. Bump MODEL default from gpt-4o-mini to gpt-4o (mini skips grounding).
  3. Replace the PROMPT block with a domain-aware version that follows
     the verified workflow: ask Knowledge Stack natural-language questions,
     follow each search hit with read(path_part_id=<hit>), cite real
     [chunk:<uuid>] markers.

The original PROMPT's first sentence is preserved as the role/goal line; the
canonical KS workflow paragraph is appended.

Run:
    uv run python scripts/bulk_refactor_recipes.py --apply
or  uv run python scripts/bulk_refactor_recipes.py --dry-run --recipe icd10_coder
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RECIPES = REPO / "recipes"

# Recipes already verified manually — leave alone.
VERIFIED = {
    "icd10_coder", "clause_extractor", "contract_renewal_checker",
    "benefits_enrollment_qa", "aml_sar_narrative", "api_deprecation_notice",
    "cashflow_anomaly_detector", "data_subject_request_responder",
    "icp_matcher", "cloud_cost_anomaly", "expense_policy_violation",
    "changelog_from_commits", "court_docket_monitor",
}

# The canonical KS workflow appended to every refactored PROMPT.
WORKFLOW = '''

KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. \
Never use folder UUIDs or path_part_id filters in your queries.
2. search_knowledge returns hits. EACH hit is a JSON object with TWO \
distinct UUIDs: chunk_id (for citation only) and path_part_id (the chunk's \
path-tree node, used for read). The text field on the hit is empty.
3. To retrieve the chunk content, call read(path_part_id=<hit.path_part_id>). \
DO NOT pass chunk_id to read — read() returns 404 on chunk_ids. If you see \
a 404, you used the wrong UUID; switch to path_part_id from the SAME hit. \
The read() output ends in a [chunk:<uuid>] marker — that uuid is the \
citation.chunk_id.
4. Build every output field ONLY from chunk text you read. Never invent \
facts. If the corpus has nothing relevant, mark the field accordingly \
(e.g. confidence='low' or 'not in corpus — upload data to proceed').
5. Populate every citation with chunk_id (verbatim from the marker), \
document_name (filename from read() output's metadata or materialized_path), \
and snippet (verbatim ≤240 chars from the chunk text). NEVER leave \
document_name or snippet blank.'''


def first_sentence(docstring: str) -> str:
    """Pull the first non-empty sentence from a docstring."""
    text = docstring.strip().strip('"').strip("'")
    # take first paragraph
    para = text.split("\n\n")[0].replace("\n", " ").strip()
    # take first sentence
    m = re.match(r"^(.+?[.!?])(?:\s|$)", para)
    return (m.group(1) if m else para)[:400]


def refactor(src: str, recipe_name: str) -> tuple[str, list[str]]:
    """Return (new_src, change_log)."""
    changes: list[str] = []
    out = src

    # 1. Remove CORPUS = os.environ.get(...) line(s).
    corpus_re = re.compile(
        r"^CORPUS\s*=\s*os\.environ\.get\([^)]+\)\s*\n",
        re.MULTILINE,
    )
    if corpus_re.search(out):
        out = corpus_re.sub("", out)
        changes.append("removed CORPUS = os.environ.get(...) line")

    # 2. Bump MODEL default from gpt-4o-mini to gpt-4o.
    if "gpt-4o-mini" in out:
        out = out.replace("'gpt-4o-mini'", "'gpt-4o'").replace(
            '"gpt-4o-mini"', '"gpt-4o"'
        )
        changes.append("bumped MODEL default to gpt-4o")

    # 3. Rewrite PROMPT. Preserve original goal sentence; append workflow.
    prompt_re = re.compile(
        r'(^PROMPT\s*=\s*\()([\s\S]+?)(\)\s*$)',
        re.MULTILINE,
    )
    m = prompt_re.search(out)
    if m:
        original_body = m.group(2)
        # Try to preserve the *first* string literal in the prompt as goal text.
        lit_re = re.compile(r'(?:f?"([^"]+)"|f?\'([^\']+)\')')
        first_lit_m = lit_re.search(original_body)
        if first_lit_m:
            goal = (first_lit_m.group(1) or first_lit_m.group(2)).strip()
            # Strip any 'path_part_id={CORPUS}' fragments from goal text.
            goal = re.sub(r"path_part_id=\{?CORPUS\}?", "your tenant", goal)
            goal = re.sub(r"\s+", " ", goal).strip()
            # Use a triple-quoted string so embedded newlines are valid Python.
            triple = '"""'
            new_assignment = (
                f"PROMPT = {triple}{goal}\n{WORKFLOW.strip()}\n{triple}\n"
            )
            out = out[: m.start()] + new_assignment + out[m.end():]
            changes.append("rewrote PROMPT with verified workflow")

    # 4. If recipe.py mentions {CORPUS} in PROMPT (after rewrite shouldn't), warn.
    if "{CORPUS}" in out or "path_part_id={CORPUS}" in out:
        changes.append("WARN: still references CORPUS after rewrite")

    return out, changes


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apply", action="store_true",
                   help="Write changes to disk (default: dry-run).")
    p.add_argument("--recipe", help="Only process this recipe directory name.")
    args = p.parse_args()

    targets: list[Path] = []
    for d in sorted(RECIPES.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        if args.recipe and d.name != args.recipe:
            continue
        if d.name in VERIFIED:
            continue
        rp = d / "recipe.py"
        if rp.exists():
            targets.append(rp)

    print(f"# {len(targets)} recipe(s) to refactor", file=sys.stderr)
    n_changed = 0
    for rp in targets:
        src = rp.read_text()
        new_src, changes = refactor(src, rp.parent.name)
        if not changes:
            print(f"  {rp.parent.name}: no changes", file=sys.stderr)
            continue
        n_changed += 1
        print(f"  {rp.parent.name}: {', '.join(changes)}", file=sys.stderr)
        if args.apply:
            rp.write_text(new_src)
    print(f"# {n_changed} recipe(s) {'patched' if args.apply else 'would change'}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
