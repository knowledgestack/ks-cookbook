"""CLI entry for the FOIA response drafter flagship."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from foia_response_drafter.agent import draft_foia_response, model_id_default


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Draft a FOIA response letter with exemption analysis."
    )
    parser.add_argument(
        "--request",
        required=True,
        help="The FOIA request text to respond to.",
    )
    parser.add_argument(
        "--corpus-folder",
        default=os.environ.get(
            "CORPUS_FOLDER_ID", "7b5ff225-9401-5f0d-a5b9-16b9106ec759"
        ),
    )
    parser.add_argument(
        "--model",
        default=model_id_default(),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("foia-response.md"),
    )
    args = parser.parse_args()

    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set.")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set.")

    memo = asyncio.run(
        draft_foia_response(
            request_text=args.request,
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
