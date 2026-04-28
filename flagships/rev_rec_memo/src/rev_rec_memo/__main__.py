"""CLI entry for the rev-rec-memo flagship."""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from rev_rec_memo.agent import draft_memo
from rev_rec_memo.writer import write_memo

DEFAULT_INPUT = (
    Path(__file__).resolve().parents[2] / "sample_inputs" / "globex_contract.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Produce an ASC 606 rev-rec memo grounded in seeded policy."
    )
    parser.add_argument(
        "--in",
        dest="in_path",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to a JSON file with {customer, product, contract_summary, "
        "total_contract_value_usd}.",
    )
    parser.add_argument(
        "--corpus-folder",
        default=os.environ.get(
            "CORPUS_FOLDER_ID",
            "fee9b054-719f-5033-a268-2ff427ad4600",
        ),
        help="folder_id of the accounting corpus in your KS tenant.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("rev-rec-memo.md"),
        help="Output markdown path (default: rev-rec-memo.md).",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("REV_REC_MODEL", "openai:gpt-4o"),
        help="pydantic-ai model id (default: openai:gpt-4o).",
    )
    args = parser.parse_args()

    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set.")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set.")
    if not args.in_path.is_file():
        sys.exit(f"Input file not found: {args.in_path}")

    payload = json.loads(args.in_path.read_text())
    customer = payload["customer"]
    product = payload["product"]
    contract_summary = payload["contract_summary"]

    memo = asyncio.run(
        draft_memo(
            customer=customer,
            product=product,
            contract_summary=contract_summary,
            corpus_folder_id=args.corpus_folder,
            model=args.model,
        )
    )
    if "total_contract_value_usd" in payload:
        memo.total_contract_value_usd = float(payload["total_contract_value_usd"])
    write_memo(memo, args.out)
    n_cites = len(memo.citations)
    print(
        f"Drafted ASC 606 memo for {customer} / {product} — "
        f"{len(memo.steps)} steps, {n_cites} citations. Wrote: {args.out}"
    )


if __name__ == "__main__":
    main()
