"""CLI entry for the zoning compliance check demo."""


import argparse
import asyncio
import os
import sys
from pathlib import Path

from zoning_compliance_check.agent import check_zoning


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Check zoning compliance for a proposed use against "
            "Austin TX LDC."
        )
    )
    parser.add_argument(
        "--address",
        default="2100 S Congress Ave, Austin, TX 78704",
        help="Street address of the property.",
    )
    parser.add_argument(
        "--zone-district",
        default="GR",
        help="Zoning district code (default: GR).",
    )
    parser.add_argument(
        "--proposed-use",
        default="outdoor entertainment venue",
        help="Proposed use to check.",
    )
    parser.add_argument(
        "--corpus-folder",
        default=os.environ.get("CORPUS_FOLDER_ID", ""),
        help="Folder id containing the zoning corpus.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("ZONING_MODEL", "gpt-4o"),
        help="OpenAI model (default: gpt-4o).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("zoning-compliance.md"),
        help="Output markdown file (default: zoning-compliance.md).",
    )
    args = parser.parse_args()

    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set. See the README.")
    memo = asyncio.run(
        check_zoning(
            address=args.address,
            zone_district=args.zone_district,
            proposed_use=args.proposed_use,
            corpus_folder_id=args.corpus_folder or None,
            model=args.model,
        )
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(memo, encoding="utf-8")
    cite_count = memo.count("[chunk:")
    print(
        f"Wrote {args.out} -- {len(memo)} chars, "
        f"{cite_count} chunk citation(s)."
    )


if __name__ == "__main__":
    main()
