#!/usr/bin/env python3
"""Generate _Sidebar.md for the GitHub Wiki from the wiki structure.

Walks the published wiki directory (after publish_wiki.sh has copied
docs/wiki/ in and renamed README.md → Home.md) and emits a sidebar that
matches the on-disk hierarchy — Home, top-level pages, then nested
sections (Frameworks, Book/Flagships, Book/Recipes).
"""

from __future__ import annotations

import argparse
from pathlib import Path

# Order top-level pages so the sidebar reads sensibly. Anything not listed
# is appended alphabetically.
TOP_ORDER = [
    "Home",
    "overview",
    "quickstart",
    "connecting",
    "frameworks",
    "mcp-tools",
    "configuration",
    "seed-data",
    "writing-a-flagship",
    "writing-a-recipe",
    "troubleshooting",
]

FRAMEWORK_ORDER = [
    "pydantic-ai",
    "langchain",
    "langgraph",
    "crewai",
    "openai-agents",
    "temporal",
    "claude-desktop",
    "custom-mcp",
]


def title_case(stem: str) -> str:
    if stem == "Home":
        return "Home"
    return stem.replace("-", " ").replace("_", " ").title()


def list_md(dir_path: Path) -> list[str]:
    return sorted(p.stem for p in dir_path.glob("*.md") if not p.name.startswith("_"))


def order(items: list[str], preferred: list[str]) -> list[str]:
    seen = set()
    out: list[str] = []
    for name in preferred:
        if name in items and name not in seen:
            out.append(name)
            seen.add(name)
    for name in sorted(items):
        if name not in seen:
            out.append(name)
            seen.add(name)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path,
                    help="The published wiki dir (Home.md lives here).")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    root: Path = args.root
    lines: list[str] = ["### Knowledge Stack Cookbook", ""]

    # Top-level pages.
    top = list_md(root)
    for stem in order(top, TOP_ORDER):
        lines.append(f"- [[{title_case(stem)}|{stem}]]")

    # Frameworks subdir.
    fw = root / "frameworks"
    if fw.is_dir():
        lines += ["", "### Frameworks"]
        for stem in order(list_md(fw), FRAMEWORK_ORDER):
            lines.append(f"- [[{title_case(stem)}|frameworks/{stem}]]")

    # Book.
    book = root / "book"
    if book.is_dir():
        lines += ["", "### Cookbook book"]
        for stem in order(list_md(book), ["README", "flagships", "recipes",
                                          "flagships-by-tag"]):
            lines.append(f"- [[{title_case(stem)}|book/{stem}]]")
        flagships_dir = book / "flagships"
        if flagships_dir.is_dir():
            lines += ["", "### Flagships by vertical"]
            for stem in order(list_md(flagships_dir), []):
                lines.append(f"- [[{title_case(stem)}|book/flagships/{stem}]]")
        recipes_dir = book / "recipes"
        if recipes_dir.is_dir():
            lines += ["", "### Recipes (alphabetical)"]
            for stem in order(list_md(recipes_dir), []):
                lines.append(f"- [[Recipes {stem.upper()}|book/recipes/{stem}]]")

    args.out.write_text("\n".join(lines) + "\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
