"""CLI entry for the tax position memo flagship."""


import argparse
import asyncio
import os
import sys
from pathlib import Path

from tax_position_memo.agent import draft_tax_memo


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Draft a tax position research memo citing IRC + Treasury Regs."
    )
    parser.add_argument(
        "--question", required=True,
        help="The tax question to research.",
    )
    parser.add_argument(
        "--corpus-folder",
        default=os.environ.get("CORPUS_FOLDER_ID",
                               "e6530865-0d30-5547-ad9d-15ccc0952b6d"),
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("TAX_MEMO_MODEL", "gpt-4o"),
    )
    parser.add_argument(
        "--out", type=Path, default=Path("tax-memo.md"),
    )
    args = parser.parse_args()

    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set.")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set.")

    memo = asyncio.run(draft_tax_memo(
        args.question,
        corpus_folder_id=args.corpus_folder,
        model=args.model,
    ))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(memo, encoding="utf-8")
    cite_count = memo.count("[chunk:")
    print(f"Wrote {args.out} — {len(memo)} chars, {cite_count} chunk citation(s).")


if __name__ == "__main__":
    main()
