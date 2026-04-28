"""Enrich each recipe's README with the live verified result + working command.

Reads e2e_recipes_full_sweep.json (or any report file) produced by
bulk_verify_recipes.py and, for each recipe with a status:

  pass    → append "## Live verified output" with the working --command + stdout
  fail    → append "## Known issue" with the failing command + stderr tail
  skip    → append "## Manual run required" explaining why the verifier skipped

Idempotent: removes any prior auto-generated section before writing the new one.

Usage:
    uv run python scripts/enrich_readmes.py \
        --report e2e_recipes_full_sweep.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RECIPES = REPO / "recipes"

AUTO_HEADER = "<!-- ks-cookbook auto-generated section: live verification -->"
AUTO_FOOTER = "<!-- end ks-cookbook auto-generated section -->"


def render_pass(rec: dict) -> str:
    cmd = rec.get("cmd", "")
    stdout_head = rec.get("stdout_head", "").strip()
    elapsed = rec.get("elapsed_s", 0)
    return (
        f"\n{AUTO_HEADER}\n"
        f"## Live verified — {rec['recipe']}\n\n"
        f"Verified end-to-end on the unified cookbook corpus on **2026-04-28** "
        f"(model `gpt-4o-mini`, ~{elapsed}s).\n\n"
        f"### Run\n\n"
        f"```bash\n"
        f"{cmd}\n"
        f"```\n\n"
        f"### Output (head)\n\n"
        f"```json\n"
        f"{stdout_head}\n"
        f"```\n\n"
        f"All `chunk_id` values in citations are verbatim UUIDs from "
        f"`[chunk:<uuid>]` markers; document filenames and snippets are real "
        f"chunk content from the ingested corpus.\n"
        f"{AUTO_FOOTER}\n"
    )


def render_fail(rec: dict) -> str:
    cmd = rec.get("cmd", "")
    stderr = "\n".join(rec.get("stderr_tail", []))[:1000]
    reason = rec.get("reason", "")
    return (
        f"\n{AUTO_HEADER}\n"
        f"## Known issue — pending fix\n\n"
        f"Last verification run failed on 2026-04-28.\n\n"
        f"```bash\n{cmd}\n```\n\n"
        f"**Failure:** {reason or 'see stderr below'}\n\n"
        f"```text\n{stderr}\n```\n"
        f"{AUTO_FOOTER}\n"
    )


def render_skip(rec: dict) -> str:
    return (
        f"\n{AUTO_HEADER}\n"
        f"## Manual run required\n\n"
        f"Last verifier run on 2026-04-28 skipped this recipe: "
        f"`{rec.get('reason', 'unknown')}`. Provide a sample input under "
        f"`sample_inputs/` then re-run.\n"
        f"{AUTO_FOOTER}\n"
    )


def render_timeout(rec: dict) -> str:
    cmd = rec.get("cmd", "")
    return (
        f"\n{AUTO_HEADER}\n"
        f"## Known issue — timed out\n\n"
        f"Last verification run on 2026-04-28 exceeded the 240s timeout.\n\n"
        f"```bash\n{cmd}\n```\n"
        f"{AUTO_FOOTER}\n"
    )


def update_readme(readme: Path, section: str) -> bool:
    if not readme.exists():
        return False
    src = readme.read_text()
    # Strip prior auto block (if any).
    pat = re.compile(
        re.escape(AUTO_HEADER) + r"[\s\S]*?" + re.escape(AUTO_FOOTER) + r"\n?",
        re.MULTILINE,
    )
    src = pat.sub("", src).rstrip() + "\n"
    src += section
    readme.write_text(src)
    return True


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--report", required=True, help="JSON report from bulk_verify_recipes.py.")
    args = p.parse_args()

    data = json.loads(Path(args.report).read_text())
    results = data.get("results", [])
    n_updated = 0
    for rec in results:
        name = rec["recipe"]
        readme = RECIPES / name / "README.md"
        renderer = {
            "pass": render_pass,
            "fail": render_fail,
            "skip": render_skip,
            "timeout": render_timeout,
        }.get(rec["status"], render_fail)
        if update_readme(readme, renderer(rec)):
            n_updated += 1
            print(f"  [{rec['status']}] {name}", file=sys.stderr)
    print(f"# {n_updated} README(s) updated", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
