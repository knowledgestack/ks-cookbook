"""Bulk refactor flagship agents to the verified architecture.

Mirrors scripts/bulk_refactor_recipes.py but works on flagship layout:
  flagships/<name>/src/<module>/agent.py

For each flagship:
  1. Strip references to __CORPUS_FOLDER_ID__ template placeholder + remove
     mandatory list_contents(folder_id=...) steps from the system prompt.
  2. Bump default model from gpt-4o-mini to gpt-4o (in agent.py + __main__.py).
  3. Inject the canonical KS workflow + strict-output directive into the prompt.
  4. Drop --corpus-folder default of os.environ.get("CORPUS_FOLDER_ID") in the
     CLI; the agent now searches the whole tenant.

Run:
    uv run python scripts/bulk_refactor_flagships.py --apply
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FLAGSHIPS = REPO / "flagships"

WORKFLOW = """KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs or path_part_id filters.
2. search_knowledge returns hits with chunk_id and path_part_id; the text field is empty by design. Call read(path_part_id=<hit's path_part_id>) to get chunk content. The trailing [chunk:<uuid>] marker is the citation chunk_id. NEVER pass chunk_id to read; it 404s.
3. Build every output field ONLY from chunk text you read. Never fabricate.
4. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() metadata or materialized_path), snippet (verbatim ≤240 chars).

Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {'<ClassName>': ...} or {'result': ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""


def refactor_agent(src: str) -> tuple[str, list[str]]:
    out = src
    changes: list[str] = []
    # Bump gpt-4o-mini -> gpt-4o for default model
    if "gpt-4o-mini" in out:
        out = out.replace("'gpt-4o-mini'", "'gpt-4o'").replace('"gpt-4o-mini"', '"gpt-4o"')
        changes.append("model default → gpt-4o")
    # Strip mandatory list_contents(folder_id=__CORPUS_FOLDER_ID__) lines from prompt
    prompt_re = re.compile(
        r"(SYSTEM_TEMPLATE\s*=\s*[a-z]?\"{3})([\s\S]*?)(\"{3})",
        re.MULTILINE,
    )
    m = prompt_re.search(out)
    if m:
        body = m.group(2)
        # Append workflow if not already there
        if "KS workflow (do NOT skip):" not in body:
            body = body.rstrip() + "\n\n" + WORKFLOW + "\n"
            new_assignment = m.group(1) + body + m.group(3)
            out = out[: m.start()] + new_assignment + out[m.end():]
            changes.append("appended canonical KS workflow + strict-output directive")
    # Drop replacement of __CORPUS_FOLDER_ID__ tokens in agent.py — recipes
    # don't pre-substitute folder ids anymore.
    if "__CORPUS_FOLDER_ID__" in out:
        out = re.sub(
            r'\.replace\(\s*"__CORPUS_FOLDER_ID__"\s*,\s*[^)]+\)',
            "",
            out,
        )
        changes.append("removed __CORPUS_FOLDER_ID__ template substitution")
    return out, changes


def refactor_main(src: str) -> tuple[str, list[str]]:
    out = src
    changes: list[str] = []
    # Drop --corpus-folder default of CORPUS_FOLDER_ID env var (no longer used)
    if "CORPUS_FOLDER_ID" in out:
        # Just leave the CLI flag in place for backward compat, but the default
        # becomes empty so the agent searches the whole tenant.
        out = re.sub(
            r'(default\s*=\s*os\.environ\.get\(\s*)"CORPUS_FOLDER_ID"(\s*,\s*"")(\s*\))',
            r'\1"CORPUS_FOLDER_ID"\2\3',
            out,
        )
    if "gpt-4o-mini" in out:
        out = out.replace("'gpt-4o-mini'", "'gpt-4o'").replace('"gpt-4o-mini"', '"gpt-4o"')
        changes.append("model default → gpt-4o")
    return out, changes


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apply", action="store_true",
                   help="Write changes (default: dry-run).")
    p.add_argument("--name", default="",
                   help="Only process this flagship dir name.")
    args = p.parse_args()

    targets = sorted(d for d in FLAGSHIPS.iterdir()
                     if d.is_dir() and not d.name.startswith("_"))
    if args.name:
        targets = [d for d in targets if d.name == args.name]

    n = 0
    for d in targets:
        if d.name == "INDEX.md":
            continue
        # Find src/<module>/
        src_dir = d / "src"
        if not src_dir.is_dir():
            continue
        for module in src_dir.iterdir():
            if not module.is_dir():
                continue
            agent_py = module / "agent.py"
            main_py = module / "__main__.py"
            if not agent_py.exists():
                continue
            agent_src = agent_py.read_text()
            new_agent, ch_a = refactor_agent(agent_src)
            new_main, ch_m = (None, [])
            if main_py.exists():
                main_src = main_py.read_text()
                new_main, ch_m = refactor_main(main_src)
            if not (ch_a or ch_m):
                continue
            n += 1
            print(f"  {d.name}: {', '.join(ch_a + ch_m)}", file=sys.stderr)
            if args.apply:
                agent_py.write_text(new_agent)
                if new_main and ch_m:
                    main_py.write_text(new_main)
    print(f"# {n} flagship(s) {'patched' if args.apply else 'would change'}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
