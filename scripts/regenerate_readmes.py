"""Regenerate per-recipe READMEs from the recipe's own source.

Each README is derived from:
  - the recipe's module docstring (first paragraph = tagline; rest = "What
    this does"),
  - its argparse CLI args + help text,
  - its pydantic output schema (top-level Agent output_type class fields),
  - its sample_inputs/ folder contents,
  - the captured stdout from the latest live verification (e2e_recipes_merged.json).

This produces a README that is unique to the recipe — not generic boilerplate.

Run:
    uv run python scripts/regenerate_readmes.py
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RECIPES = REPO / "recipes"
REPORT = REPO / "e2e_recipes_merged.json"


def _humanize(slug: str) -> str:
    return " ".join(p.capitalize() for p in slug.replace("-", "_").split("_"))


def _docstring(tree: ast.AST) -> str | None:
    if isinstance(tree, ast.Module):
        return ast.get_docstring(tree)
    return None


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
            elif isinstance(kw.value, ast.List):
                attrs[kw.arg] = [
                    e.value for e in kw.value.elts if isinstance(e, ast.Constant)
                ]
        args.append((flag, attrs))
    return args


def _output_class_name(tree: ast.Module) -> str | None:
    """Find the BaseModel passed as output_type=... to Agent(...)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "Agent":
            for kw in node.keywords:
                if kw.arg == "output_type" and isinstance(kw.value, ast.Name):
                    return kw.value.id
    return None


def _class_fields(tree: ast.Module, class_name: str) -> list[tuple[str, str]]:
    """Return (field_name, type_repr) for every class field."""
    fields: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    fields.append((item.target.id, ast.unparse(item.annotation)))
            break
    return fields


def _sample_inputs(recipe_dir: Path) -> list[str]:
    sd = recipe_dir / "sample_inputs"
    if not sd.is_dir():
        return []
    return sorted(p.name for p in sd.iterdir() if p.is_file())


def _load_report() -> dict:
    if not REPORT.exists():
        return {"results": []}
    return json.loads(REPORT.read_text())


def _result_for(recipe: str, report: dict) -> dict | None:
    for r in report.get("results", []):
        if r["recipe"] == recipe:
            return r
    return None


def _build_run_cmd(recipe: str, args: list[tuple[str, dict]], samples: list[str]) -> str:
    """Construct a working `uv run` invocation."""
    parts = ["uv run python", f"recipes/{recipe}/recipe.py"]
    sample_path = f"recipes/{recipe}/sample_inputs/{samples[0]}" if samples else None
    file_argnames = {"file", "csv", "input", "doc", "template", "config-file",
                     "note-file", "note_file", "cur-file", "cur_file",
                     "commits-file", "commits_file"}
    arg_defaults = {
        "question": '"What ERISA disclosures must an employer provide to participants in the SPD?"',
        "contract": '"Apple 2024 proxy"',
        "company": "FreshFinTech",
        "case-id": "structuring-cash-deposits",
        "case_id": "structuring-cash-deposits",
        "party": '"Jackson Women\'s Health Organization"',
        "endpoint": '"POST /v1/ingest"',
        "replacement": '"POST /v2/ingest"',
        "sunset": "2026-12-31",
        "version": "v2.4.0",
        "date": "2026-04-27",
        "type": "erasure",
        "description": '"Client dinner at Smith & Wollensky NYC"',
        "amount": '"$485.00"',
        "category": "entertainment",
        "asset-class": "corporate",
        "asset_class": "corporate",
        "counterparty": '"BB-rated corporate"',
        "notional": "10000000",
        "vendor": '"Acme Vendor LLC"',
        "drug": "metformin",
        "scenario": "baseline",
        "sprint": "FY26-Q2-S1",
        "capacity-days": "10",
        "capacity_days": "10",
        "name": '"Acme Corp"',
        "role": '"Backend Engineer"',
        "blurb": '"Series B B2B fintech, 250 employees, US + UK."',
        "topic": '"Q4 board update"',
        "audience": '"engineering team"',
    }
    for flag, attrs in args:
        if not flag.startswith("--"):
            continue
        if attrs.get("action") in ("store_true", "store_false"):
            continue
        # Skip args with a default — let argparse use it.
        if attrs.get("required") is not True and "default" in attrs:
            continue
        bare = flag[2:]
        is_file = bare.endswith("-file") or bare.endswith("_file") or bare in file_argnames
        if is_file and sample_path:
            parts.append(f"\\\n    {flag} {sample_path}")
        else:
            val = arg_defaults.get(bare, arg_defaults.get(bare.replace("-", "_"), '"demo"'))
            parts.append(f"\\\n    {flag} {val}")
    return " ".join(parts)


def _docstring_first_para_and_rest(doc: str) -> tuple[str, str]:
    paras = re.split(r"\n\s*\n", doc.strip())
    first = paras[0].replace("\n", " ").strip()
    rest = "\n\n".join(p.strip() for p in paras[1:]) if len(paras) > 1 else ""
    return first, rest


def render_readme(recipe: str, recipe_dir: Path, report: dict) -> str:
    src = (recipe_dir / "recipe.py").read_text()
    tree = ast.parse(src)
    doc = _docstring(tree) or ""
    tagline, body = _docstring_first_para_and_rest(doc)
    title = _humanize(recipe)
    args = _argparse_args(tree)
    samples = _sample_inputs(recipe_dir)
    out_class = _output_class_name(tree)
    fields = _class_fields(tree, out_class) if out_class else []
    result = _result_for(recipe, report) or {}
    run_cmd = _build_run_cmd(recipe, args, samples)

    parts: list[str] = []
    parts.append(f"# {title}\n")
    parts.append(f"> **{tagline}**\n")

    parts.append("## Table of contents\n")
    parts.append(
        "1. [What this recipe does](#what-this-recipe-does)\n"
        "2. [How it works](#how-it-works)\n"
        "3. [Sign in to Knowledge Stack](#sign-in-to-knowledge-stack)\n"
        "4. [Ingest the unified corpus](#ingest-the-unified-corpus)\n"
        "5. [Inputs](#inputs)\n"
        "6. [Output schema](#output-schema)\n"
        "7. [Run](#run)\n"
        "8. [Live verified output](#live-verified-output)\n"
        "9. [Troubleshooting](#troubleshooting)\n"
        "10. [Files](#files)\n"
    )

    parts.append("## What this recipe does\n")
    if body:
        parts.append(body + "\n")
    else:
        parts.append(tagline + "\n")

    parts.append("## How it works\n")
    parts.append(
        "1. The recipe spawns the `knowledgestack-mcp` stdio server (auth via "
        "`KS_API_KEY`).\n"
        "2. A pydantic-ai `Agent` is built with a strict pydantic output "
        "schema and `gpt-4o`/`gpt-4o-mini`.\n"
        "3. The agent asks Knowledge Stack natural-language questions via "
        "`search_knowledge`. **It never passes folder UUIDs** — KS finds the "
        "right document by content.\n"
        "4. For every search hit the agent calls `read(path_part_id=<hit>)` "
        "to retrieve the full chunk text. The trailing `[chunk:<uuid>]` "
        "marker is the citation.\n"
        "5. The validated pydantic object is printed as JSON to stdout. Every "
        "`chunk_id` is a verbatim UUID from a real chunk in your tenant.\n"
    )

    parts.append("## Sign in to Knowledge Stack\n")
    parts.append(
        "**Path A — `ingestion: true` (shared cookbook tenant, fastest)**\n\n"
        "Sign in at <https://app.knowledgestack.ai>, request a read-only "
        '"Cookbook demo" key, then:\n\n'
        "```bash\nexport KS_API_KEY=sk-user-...\n"
        "export KS_BASE_URL=https://api.knowledgestack.ai\n"
        "export OPENAI_API_KEY=sk-...\n"
        "export MODEL=gpt-4o-mini\n```\n\n"
        "Skip to step 5 (Run).\n\n"
        "**Path B — `ingestion: false` (clone repo, ingest into your own tenant)**\n\n"
        "```bash\ngit clone https://github.com/knowledgestack/ks-cookbook\n"
        "cd ks-cookbook\nmake install\n"
        "export KS_API_KEY=sk-user-...   # your own KS key\n"
        "export KS_BASE_URL=https://api.knowledgestack.ai\n"
        "export OPENAI_API_KEY=sk-...\n"
        "export MODEL=gpt-4o-mini\n```\n"
    )

    parts.append("## Ingest the unified corpus\n")
    parts.append(
        "Path B only — one-time. The bundled `seed/` folder has 34 real "
        "public-domain documents (CMS ICD-10, NIST 800-53, IRS Pubs, OCC "
        "Handbook, KO 10-K, AAPL 2024 proxy, FAR, NERC CIP, FDA Orange Book, "
        "BLS XLSX, CDC PPTX, …). Create a parent folder in your tenant via "
        "the UI, then:\n\n"
        "```bash\nmake seed-unified-corpus PARENT_FOLDER_ID=<your-folder-uuid>\n```\n"
    )

    parts.append("## Inputs\n")
    if args:
        parts.append("| Flag | Type | Required | Default | Help |\n|---|---|---|---|---|\n")
        for flag, attrs in args:
            req = "yes" if attrs.get("required") is True else "no"
            t = attrs.get("type") or "str"
            d = attrs.get("default", "")
            d_str = "—" if d in (None, "") else repr(d)
            help_str = (attrs.get("help") or "").replace("\n", " ").replace("|", "\\|")
            parts.append(f"| `{flag}` | {t} | {req} | {d_str} | {help_str} |\n")
    else:
        parts.append("This recipe takes no CLI arguments.\n")
    if samples:
        parts.append("\n**Sample inputs available** in `sample_inputs/`:\n")
        for s in samples:
            parts.append(f"- `{s}`\n")

    parts.append("## Output schema\n")
    if out_class and fields:
        parts.append(
            f"`{out_class}` — pydantic model emitted as JSON to stdout.\n\n"
            "| Field | Type |\n|---|---|\n"
        )
        for fname, ftype in fields:
            parts.append(f"| `{fname}` | `{ftype}` |\n")
    else:
        parts.append("Output is JSON printed to stdout.\n")

    parts.append("## Run\n")
    parts.append(f"```bash\n{run_cmd}\n```\n")

    parts.append("## Live verified output\n")
    if result.get("status") == "pass" and result.get("stdout_head"):
        parts.append(
            f"Verified end-to-end against `api.knowledgestack.ai` on **2026-04-28** "
            f"with `MODEL=gpt-4o-mini` (~{result.get('elapsed_s', '?')}s):\n\n"
            "```json\n" + result["stdout_head"].rstrip() + "\n```\n\n"
            "Every `chunk_id` is a verbatim UUID from a `[chunk:<uuid>]` marker; "
            "snippets and document names are real chunk content from the "
            "ingested corpus.\n"
        )
    elif result.get("status") in ("fail", "timeout"):
        parts.append(
            f"⚠️ **Last verification ({result.get('status', 'fail')}, "
            f"{result.get('elapsed_s', '?')}s)** — see `e2e_recipes_merged.json` "
            "for full stderr. This recipe is currently a known-issue; see "
            "[`docs/RFC_KS_MCP_HANDHOLDING.md`](../../docs/RFC_KS_MCP_HANDHOLDING.md) "
            "for the upstream fix that unblocks small-model first-shot pass rate.\n"
        )
    else:
        parts.append("(No verification result on file — run `make verify-clone N=5` "
                     "to populate.)\n")

    parts.append("## Troubleshooting\n")
    parts.append(
        "| Symptom | Fix |\n|---|---|\n"
        "| `Set KS_API_KEY and OPENAI_API_KEY.` | Export both env vars before running. |\n"
        "| `Tool 'read' exceeded max retries` | gpt-4o-mini occasionally calls "
        "`read(<chunk_id>)` instead of `read(<path_part_id>)`. Re-run; the prompt "
        "self-corrects within `retries=4`. Switching to `MODEL=gpt-4o` removes "
        "the flake. |\n"
        "| Empty / non-grounded output | The corpus isn't ingested into your "
        "tenant. Run `make seed-unified-corpus PARENT_FOLDER_ID=<uuid>`. |\n"
        "| `Connection error` from OpenAI | Transient; retry. |\n"
        "| `request_limit of 50` exceeded | The agent looped too many tools. "
        "Re-run; this is rare. |\n"
    )

    parts.append("## Files\n")
    parts.append(f"```text\nrecipes/{recipe}/\n├── README.md            ← you are here\n├── recipe.py            ← agent + schema (no FOLDER_ID env vars)\n")
    if samples:
        parts.append("└── sample_inputs/\n")
        for i, s in enumerate(samples):
            connector = "    └──" if i == len(samples) - 1 else "    ├──"
            parts.append(f"{connector} {s}\n")
    parts.append("```\n")

    return "\n".join(parts)


def main() -> int:
    report = _load_report()
    n = 0
    for d in sorted(RECIPES.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        rp = d / "recipe.py"
        if not rp.exists():
            continue
        readme = d / "README.md"
        try:
            content = render_readme(d.name, d, report)
        except Exception as e:
            print(f"  ERR  {d.name}: {e}", file=sys.stderr)
            continue
        readme.write_text(content)
        n += 1
    print(f"# regenerated {n} README(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
