"""CLI entry for the claim-adjudication-memo demo."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from claim_adjudication_memo.agent import draft_memo


def _load_narrative(in_path: Path | None) -> str:
    if in_path is not None:
        return in_path.read_text(encoding="utf-8")
    default = Path(__file__).resolve().parents[2] / "sample_inputs" / "claim.txt"
    return default.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Draft a cited coverage-analysis memo from a P&C claim narrative."
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
        default=Path("claim-memo.md"),
        help="Output markdown file (default: claim-memo.md).",
    )
    parser.add_argument(
        "--corpus-folder",
        default=os.environ.get("CORPUS_FOLDER_ID", ""),
        help="Folder id containing the insurance corpus.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("CLAIM_MEMO_MODEL", "gpt-4o"),
        help="OpenAI model (default: gpt-4o).",
    )
    args = parser.parse_args()

    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set. See the README.")
    if not args.corpus_folder:
        sys.exit(
            "--corpus-folder (or CORPUS_FOLDER_ID env var) is required. "
            "Run `make demo-claim-memo-setup` first."
        )

    narrative = _load_narrative(args.in_path)
    memo = asyncio.run(
        draft_memo(
            narrative,
            corpus_folder_id=args.corpus_folder,
            model=args.model,
        )
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(memo, encoding="utf-8")
    cite_count = memo.count("[chunk:")
    print(f"Wrote {args.out} — {len(memo)} chars, {cite_count} chunk citation(s).")


if __name__ == "__main__":
    main()
