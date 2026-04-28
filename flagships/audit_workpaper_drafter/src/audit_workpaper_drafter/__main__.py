"""CLI entry for the audit-workpaper-drafter flagship."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from audit_workpaper_drafter.agent import draft_workpaper

DEFAULT_REQUEST = (
    "Draft an audit workpaper for Accounts Receivable. "
    "The trial balance shows AR at $1,240,000 as of December 31, 2025. "
    "Perform confirmation, analytical procedures, and aging analysis. "
    "The client is Acme SaaS, Inc. Period: FY2025."
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Draft a cited audit workpaper for a GL account balance."
    )
    parser.add_argument(
        "--account-request",
        default=None,
        help="Natural-language description of the account and balance to audit. "
        "Defaults to an AR audit request.",
    )
    parser.add_argument(
        "--in",
        dest="in_path",
        type=Path,
        default=None,
        help="File containing the account audit request.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("audit-workpaper.md"),
        help="Output markdown file (default: audit-workpaper.md).",
    )
    parser.add_argument(
        "--corpus-folder",
        default=os.environ.get("CORPUS_FOLDER_ID", ""),
        help="Folder id containing the accounting-audit corpus.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("AUDIT_WP_MODEL", "gpt-4o"),
        help="OpenAI model (default: gpt-4o).",
    )
    args = parser.parse_args()

    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set. See the README.")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set.")
    if not args.corpus_folder:
        sys.exit(
            "--corpus-folder (or CORPUS_FOLDER_ID env var) is required. "
            "Run the seed script first."
        )

    if args.in_path is not None:
        request = args.in_path.read_text(encoding="utf-8")
    elif args.account_request is not None:
        request = args.account_request
    else:
        request = DEFAULT_REQUEST

    workpaper = asyncio.run(
        draft_workpaper(
            request,
            corpus_folder_id=args.corpus_folder,
            model=args.model,
        )
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(workpaper, encoding="utf-8")
    cite_count = workpaper.count("[chunk:")
    print(
        f"Wrote {args.out} -- {len(workpaper)} chars, {cite_count} chunk citation(s)."
    )


if __name__ == "__main__":
    main()
