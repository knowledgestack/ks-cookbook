"""Regenerate per-flagship READMEs from the flagship's source.

Each flagship lives under flagships/<name>/src/<module>/ with at least
agent.py + __main__.py + schema.py. This script:

- Reads the agent.py / __main__.py docstrings + argparse args.
- Reads the SYSTEM_TEMPLATE / PROMPT for the flagship's domain description.
- Reads schema.py for the output type (pydantic class).
- Reads the e2e-report.json verdict for that flagship.
- Builds a detailed README that actually explains what THIS flagship does.

Run: uv run python scripts/regenerate_flagship_readmes.py
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FLAGSHIPS = REPO / "flagships"
REPORT = REPO / "e2e-report.json"


def _humanize(s: str) -> str:
    return " ".join(p.capitalize() for p in s.replace("-", "_").split("_"))


def _docstring(tree: ast.Module) -> str:
    return ast.get_docstring(tree) or ""


def _argparse_args(tree: ast.Module) -> list[tuple[str, dict]]:
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


def _output_class(tree: ast.Module) -> str | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "Agent":
            for kw in node.keywords:
                if kw.arg == "output_type" and isinstance(kw.value, ast.Name):
                    return kw.value.id
    return None


def _class_fields(tree: ast.Module, name: str) -> list[tuple[str, str]]:
    fields: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    fields.append((item.target.id, ast.unparse(item.annotation)))
            break
    return fields


def _make_demo_target(flagship: str) -> str:
    """Read the Makefile to find the demo-* target for this flagship."""
    mf = (REPO / "Makefile").read_text()
    # heuristic: scan demo-* targets; match by package name in the body.
    pkg = "ks-cookbook-" + flagship.replace("_", "-")
    for m in re.finditer(r"^(demo-[a-z0-9-]+):", mf, re.MULTILINE):
        target = m.group(1)
        body_start = m.end()
        body_end = mf.find("\ndemo-", body_start)
        if body_end == -1:
            body_end = len(mf)
        body = mf[body_start:body_end]
        if pkg in body or flagship.replace("_", "-") in target:
            return target
    return f"demo-{flagship.replace('_','-')}"


def _verdict_for(flagship: str, report: list[dict]) -> dict | None:
    for r in report:
        if r.get("kind") == "flagship" and r.get("name") in (flagship, flagship.replace("_", "-")):
            return r
    return None


def render(flagship: str, fdir: Path, report: list[dict]) -> str | None:
    src_root = fdir / "src"
    if not src_root.is_dir():
        return None
    modules = [p for p in src_root.iterdir() if p.is_dir() and (p / "agent.py").exists()]
    if not modules:
        return None
    module = modules[0]
    agent_py = module / "agent.py"
    main_py = module / "__main__.py"

    agent_tree = ast.parse(agent_py.read_text())
    main_tree = ast.parse(main_py.read_text()) if main_py.exists() else None

    agent_doc = _docstring(agent_tree)
    main_doc = _docstring(main_tree) if main_tree else ""
    desc = main_doc or agent_doc
    paras = re.split(r"\n\s*\n", desc.strip()) if desc else [_humanize(flagship)]
    tagline = paras[0].replace("\n", " ").strip() if paras else _humanize(flagship)
    body = "\n\n".join(p.strip() for p in paras[1:]) if len(paras) > 1 else ""

    args = _argparse_args(main_tree) if main_tree else []
    out_class = _output_class(agent_tree)
    schema_path = module / "schema.py"
    fields: list[tuple[str, str]] = []
    if out_class and schema_path.exists():
        fields = _class_fields(ast.parse(schema_path.read_text()), out_class)

    demo = _make_demo_target(flagship)
    verdict = _verdict_for(flagship, report) or {}

    parts: list[str] = []
    parts.append(f"# {_humanize(flagship)}\n")
    parts.append(f"> **{tagline}**\n")

    parts.append("## Table of contents\n")
    parts.append(
        "1. [What this flagship does](#what-this-flagship-does)\n"
        "2. [How it works](#how-it-works)\n"
        "3. [Sign in to Knowledge Stack](#sign-in-to-knowledge-stack)\n"
        "4. [Ingest the unified corpus](#ingest-the-unified-corpus)\n"
        "5. [Inputs](#inputs)\n"
        "6. [Output schema](#output-schema)\n"
        "7. [Run](#run)\n"
        "8. [Verification status](#verification-status)\n"
        "9. [Files](#files)\n"
    )

    parts.append("## What this flagship does\n")
    if body:
        parts.append(body + "\n")
    else:
        parts.append(tagline + "\n")

    parts.append("## How it works\n")
    parts.append(
        "1. The flagship spawns the `knowledgestack-mcp` stdio server (auth via `KS_API_KEY`).\n"
        "2. A pydantic-ai `Agent` (or raw OpenAI tool-calling loop in some flagships) is built with a strict pydantic output schema.\n"
        "3. The agent asks Knowledge Stack natural-language questions via "
        "`search_knowledge` — no folder UUIDs are needed; KS finds the right document by content.\n"
        "4. For every search hit the agent calls `read(path_part_id=<hit>)` to fetch the chunk text and the `[chunk:<uuid>]` citation marker.\n"
        "5. The validated output is rendered to a file artifact (`.md` / `.docx` / `.xlsx`) under this folder as `sample_output.<ext>`.\n"
    )

    parts.append("## Sign in to Knowledge Stack\n")
    parts.append(
        "**Path A — `ingestion: true` (shared cookbook tenant, fastest)**\n\n"
        "```bash\nexport KS_API_KEY=sk-user-...\n"
        "export KS_BASE_URL=https://api.knowledgestack.ai\n"
        "export OPENAI_API_KEY=sk-...\n"
        "export MODEL=gpt-4o-mini\n```\n\n"
        "**Path B — `ingestion: false` (clone repo, ingest your own data)**\n\n"
        "```bash\ngit clone https://github.com/knowledgestack/ks-cookbook\ncd ks-cookbook\n"
        "make install\nexport KS_API_KEY=sk-user-...   # your own KS key\n"
        "export KS_BASE_URL=https://api.knowledgestack.ai\n"
        "export OPENAI_API_KEY=sk-...\n"
        "export MODEL=gpt-4o-mini\n```\n"
    )

    parts.append("## Ingest the unified corpus\n")
    parts.append(
        "Path B only — one-time. The bundled `seed/` folder has 34 real "
        "public-domain documents across 13 verticals.\n\n"
        "```bash\nmake seed-unified-corpus PARENT_FOLDER_ID=<your-folder-uuid>\n```\n"
    )

    parts.append("## Inputs\n")
    if args:
        parts.append("| Flag | Required | Default | Help |\n|---|---|---|---|\n")
        for flag, attrs in args:
            req = "yes" if attrs.get("required") is True else "no"
            d = attrs.get("default", "")
            d_str = "—" if d in (None, "") else repr(d)
            help_str = (attrs.get("help") or "").replace("\n", " ").replace("|", "\\|")
            parts.append(f"| `{flag}` | {req} | {d_str} | {help_str} |\n")
    else:
        parts.append("This flagship takes no CLI arguments (uses defaults).\n")

    sample_dir = fdir / "sample_inputs"
    if sample_dir.is_dir():
        samples = sorted(p.name for p in sample_dir.iterdir() if p.is_file())
        if samples:
            parts.append("\n**Sample inputs** in `sample_inputs/`:\n")
            for s in samples:
                parts.append(f"- `{s}`\n")

    parts.append("## Output schema\n")
    if out_class and fields:
        parts.append(
            f"`{out_class}` (in `schema.py`) — emitted as a structured artifact.\n\n"
            "| Field | Type |\n|---|---|\n"
        )
        for fname, ftype in fields:
            parts.append(f"| `{fname}` | `{ftype}` |\n")
    else:
        parts.append("Output is a Markdown / DOCX / XLSX artifact written to this folder.\n")

    parts.append("## Run\n")
    parts.append(
        f"From the repo root:\n\n"
        f"```bash\nmake {demo}\n```\n\n"
        f"Or directly:\n\n"
        f"```bash\nuv run --package ks-cookbook-{flagship.replace('_','-')} "
        f"ks-cookbook-{flagship.replace('_','-')} --help\n```\n"
    )

    parts.append("## Verification status\n")
    v = verdict.get("verdict")
    if v == "PASS":
        parts.append(
            f"✅ **Verified PASS** end-to-end on **2026-04-28** "
            f"({verdict.get('seconds', '?')}s) against `api.knowledgestack.ai`. "
            f"Output: `{verdict.get('artifact', 'sample_output.md')}` "
            f"with {verdict.get('citations_found', '?')} citations.\n"
        )
    elif v in ("EMPTY_OUTPUT",):
        parts.append(
            "⚠️ **EMPTY_OUTPUT** — last run produced an artifact but the "
            "verifier didn't find `[chunk:<uuid>]` citation markers in the "
            "stdout. The flagship may be writing markers into a binary "
            "artifact (.docx/.xlsx) where the verifier doesn't currently "
            "scan, or the agent skipped grounding. See "
            "[`docs/RFC_KS_MCP_HANDHOLDING.md`](../../docs/RFC_KS_MCP_HANDHOLDING.md).\n"
        )
    elif v == "SCHEMA_ERROR":
        parts.append(
            "🚧 **SCHEMA_ERROR** — flagship is currently a known-issue. "
            "Likely causes: stale `__CORPUS_FOLDER_ID__` references, raw "
            "OpenAI tool-calling not yet refactored to the search→read "
            "pattern, or a CLI default that requires manual setup. Tracked "
            "in the upcoming flagship sweep.\n"
        )
    elif v == "TIMEOUT":
        parts.append(
            "🚧 **TIMEOUT** — agent loop exceeded the 360s budget. "
            "Probably hit pydantic-ai's default `request_limit=50`.\n"
        )
    else:
        parts.append("(Not yet verified — run `make smoke` or `make demo-...`.)\n")

    parts.append("## Files\n")
    parts.append(f"```text\nflagships/{flagship}/\n├── README.md          ← you are here\n"
                 f"├── pyproject.toml\n"
                 f"├── sample_inputs/     (where applicable)\n"
                 f"├── sample_output.<ext> (generated by `make {demo}`)\n"
                 f"└── src/{module.name}/\n"
                 f"    ├── __main__.py    ← CLI entry\n"
                 f"    ├── agent.py       ← pydantic-ai Agent + system prompt\n"
                 f"    └── schema.py      ← pydantic output schema\n```\n")

    return "\n".join(parts)


def main() -> int:
    report = json.loads(REPORT.read_text()) if REPORT.exists() else []
    n = 0
    for d in sorted(FLAGSHIPS.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        readme = d / "README.md"
        try:
            content = render(d.name, d, report)
        except Exception as e:
            print(f"  ERR  {d.name}: {e}", file=sys.stderr)
            continue
        if content is None:
            continue
        readme.write_text(content)
        n += 1
    print(f"# regenerated {n} flagship README(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
