"""CLI entry for the research-brief demo."""


import argparse
import asyncio
import os
import sys
from pathlib import Path

from research_brief.agent import research_topic
from research_brief.docx_writer import write_docx


def _default_model() -> str:
    if os.environ.get("RESEARCH_BRIEF_MODEL"):
        return os.environ["RESEARCH_BRIEF_MODEL"]
    if os.environ.get("OPENAI_API_KEY"):
        return "openai:gpt-4o"
    return "anthropic:claude-opus-4-6"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a cited .docx research brief from your KS tenant.")
    parser.add_argument("--topic", required=True, help="Research topic to brief on.")
    parser.add_argument(
        "--out", default="brief.docx", type=Path, help="Output .docx path (default: brief.docx)."
    )
    parser.add_argument(
        "--model",
        default=_default_model(),
        help="pydantic-ai model id.",
    )
    args = parser.parse_args()

    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set. See the README.")

    brief = asyncio.run(research_topic(args.topic, model=args.model))
    write_docx(brief, args.out)
    print(f"Wrote {args.out} — {len(brief.sections)} sections, {len(brief.citations)} citations.")


if __name__ == "__main__":
    main()
