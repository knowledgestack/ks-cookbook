"""CLI entry for the subrogation opportunity review demo."""

import argparse
import os
import sys
from pathlib import Path

from subrogation_opportunity_review.agent import draft_review


def _load_claim(in_path: Path | None) -> str:
    if in_path is not None:
        return in_path.read_text(encoding="utf-8")
    default = Path(__file__).resolve().parents[2] / "sample_inputs" / "claim.txt"
    return default.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=("Assess subrogation recovery opportunity from a P&C claim.")
    )
    parser.add_argument(
        "--in",
        dest="in_path",
        type=Path,
        default=None,
        help="Claim narrative file (default: sample_inputs/claim.txt).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("subro-review.md"),
        help="Output markdown file (default: subro-review.md).",
    )
    parser.add_argument(
        "--corpus-folder",
        default=os.environ.get("CORPUS_FOLDER_ID", ""),
        help="Folder id containing the subrogation corpus.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("SUBRO_MODEL", "gpt-4o"),
        help="OpenAI model (default: gpt-4o).",
    )
    args = parser.parse_args()

    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set. See the README.")
    if not args.corpus_folder:
        sys.exit(
            "--corpus-folder (or CORPUS_FOLDER_ID env var) is required. "
            "Run the seed script first."
        )

    narrative = _load_claim(args.in_path)
    # draft_review is sync (raw OpenAI); no asyncio needed
    memo = draft_review(
        narrative,
        corpus_folder_id=args.corpus_folder,
        model=args.model,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(memo, encoding="utf-8")
    cite_count = memo.count("[chunk:")
    print(f"Wrote {args.out} -- {len(memo)} chars, {cite_count} chunk citation(s).")


if __name__ == "__main__":
    main()
