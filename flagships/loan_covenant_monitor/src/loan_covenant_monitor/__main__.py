"""Covenant compliance monitor CLI."""


import argparse
import asyncio
import os
import sys
from pathlib import Path

from loan_covenant_monitor.agent import monitor_covenants


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Monitor loan covenant compliance from KS-seeded credit "
        "agreement and quarterly financials.",
    )
    parser.add_argument(
        "--borrower",
        default="Nimbus Networks, Inc.",
        help="Borrower name (default: Nimbus Networks, Inc.).",
    )
    parser.add_argument(
        "--period",
        default="Q4 2025 / FY 2025",
        help="Reporting period (default: Q4 2025 / FY 2025).",
    )
    parser.add_argument(
        "--corpus-folder",
        default=os.environ.get("COVENANT_CORPUS_FOLDER_ID", ""),
        help="Folder.id of the covenant corpus in your KS tenant.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("MODEL", "gpt-4o"),
        help="OpenAI model (default: gpt-4o).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("covenant-report.md"),
        help="Output markdown file (default: covenant-report.md).",
    )
    args = parser.parse_args()

    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set. See the README.")
    report = asyncio.run(monitor_covenants(
        borrower=args.borrower,
        period=args.period,
        corpus_folder_id=args.corpus_folder or None,
        model=args.model,
    ))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    cite_count = report.count("[chunk:")
    print(
        f"Wrote {args.out} — {len(report)} chars, {cite_count} chunk "
        f"citation(s)."
    )


if __name__ == "__main__":
    main()
