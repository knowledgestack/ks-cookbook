"""CLI entry for the adverse-event narrative flagship."""


import argparse
import asyncio
import os
import sys
from pathlib import Path

from adverse_event_narrative.agent import draft_narrative


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Draft a CIOMS adverse-event narrative cited to drug label + PV SOP."
    )
    parser.add_argument(
        "--event", required=True,
        help="Description of the adverse event.",
    )
    parser.add_argument(
        "--drug", required=True,
        help="Drug name (e.g. semaglutide).",
    )
    parser.add_argument(
        "--corpus-folder",
        default=os.environ.get("CORPUS_FOLDER_ID", ""),
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("AE_NARRATIVE_MODEL", "gpt-4o"),
    )
    parser.add_argument(
        "--out", type=Path, default=Path("ae-narrative.md"),
    )
    args = parser.parse_args()

    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set.")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set.")

    memo = asyncio.run(draft_narrative(
        args.event, args.drug,
        corpus_folder_id=args.corpus_folder or None,
        model=args.model,
    ))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(memo, encoding="utf-8")
    cite_count = memo.count("[chunk:")
    print(f"Wrote {args.out} — {len(memo)} chars, {cite_count} chunk citation(s).")


if __name__ == "__main__":
    main()
