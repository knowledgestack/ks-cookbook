"""CLI entry for the adverse-event narrative flagship."""

import argparse
import asyncio
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from adverse_event_narrative.agent import draft_narrative  # pyright: ignore[reportImplicitRelativeImport]


@dataclass(slots=True)
class CliArgs:
    event: str
    drug: str
    corpus_folder: str
    model: str
    out: Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Draft a CIOMS adverse-event narrative cited to drug label + PV SOP."
    )
    _ = parser.add_argument(
        "--event",
        required=True,
        help="Description of the adverse event.",
    )
    _ = parser.add_argument(
        "--drug",
        required=True,
        help="Drug name (e.g. semaglutide).",
    )
    _ = parser.add_argument(
        "--corpus-folder",
        default=os.environ.get("CORPUS_FOLDER_ID", ""),
    )
    _ = parser.add_argument(
        "--model",
        default=os.environ.get("AE_NARRATIVE_MODEL", "gpt-4o"),
    )
    _ = parser.add_argument(
        "--out",
        type=Path,
        default=Path("ae-narrative.md"),
    )
    namespace = parser.parse_args()
    event = cast(str, namespace.event)
    drug = cast(str, namespace.drug)
    corpus_folder = cast(str, namespace.corpus_folder)
    model = cast(str, namespace.model)
    out = cast(str | Path, namespace.out)
    args = CliArgs(
        event=event,
        drug=drug,
        corpus_folder=corpus_folder,
        model=model,
        out=Path(out),
    )

    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set.")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set.")

    memo = asyncio.run(
        draft_narrative(
            event=args.event,
            drug=args.drug,
            corpus_folder_id=args.corpus_folder or None,
            model=args.model,
        )
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    _ = args.out.write_text(memo, encoding="utf-8")
    cite_count = memo.count("[chunk:")
    print(f"Wrote {args.out} — {len(memo)} chars, {cite_count} chunk citation(s).")


if __name__ == "__main__":
    main()
