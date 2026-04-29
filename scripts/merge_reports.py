"""Merge full sweep + retry report. Retry results override full sweep results.

Output: e2e_recipes_merged.json (suitable for enrich_readmes.py).
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def merge(*report_paths: Path) -> dict:
    """Right-most report wins per recipe."""
    by_name: dict[str, dict] = {}
    for p in report_paths:
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        for r in d.get("results", []):
            by_name[r["recipe"]] = r
    results = sorted(by_name.values(), key=lambda r: r["recipe"])
    summary = {s: sum(1 for r in results if r["status"] == s)
               for s in ("pass", "fail", "skip", "timeout")}
    return {"results": results, "summary": summary}


if __name__ == "__main__":
    out = REPO / "e2e_recipes_merged.json"
    paths = [REPO / p for p in sys.argv[1:]] or [
        REPO / "e2e_recipes_full_sweep.json",
        REPO / "e2e_recipes_retry.json",
    ]
    merged = merge(*paths)
    out.write_text(json.dumps(merged, indent=2))
    print(f"merged {len(merged['results'])} recipes — {merged['summary']}")
