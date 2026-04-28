"""CLI entry for the CSV enrichment demo."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from csv_enrichment.graph import build_graph, read_csv, write_csv


async def _run(
    in_path: Path,
    out_path: Path,
    *,
    query_column: str,
    new_column: str,
    concurrency: int,
    fail_fast: bool,
) -> None:
    fieldnames, rows = read_csv(in_path, query_column=query_column)
    if not rows:
        sys.exit(f"No rows found in {in_path}")

    graph = build_graph()
    state = await graph.ainvoke(
        {
            "rows": rows,
            "column": new_column,
            "concurrency": concurrency,
            "fail_fast": fail_fast,
            "results": {},
        }
    )

    write_csv(out_path, fieldnames, rows, state["results"], new_column)
    errors = sum(1 for v in state["results"].values() if v.startswith("ERROR:"))
    print(f"Wrote {out_path} — {len(rows)} rows, {errors} errored.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk-enrich a CSV from the KS knowledge base.")
    parser.add_argument("--in", dest="in_path", required=True, type=Path, help="Input CSV.")
    parser.add_argument("--out", required=True, type=Path, help="Output CSV.")
    parser.add_argument(
        "--query-column",
        default="query",
        help="Which CSV column to use as the KB query (default: 'query').",
    )
    parser.add_argument(
        "--column",
        default="research_summary",
        help="Name of the column to write the summary into (default: research_summary).",
    )
    parser.add_argument(
        "--concurrency", type=int, default=5, help="Max concurrent MCP calls (default: 5)."
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Abort on first row failure (default: write ERROR: into the cell and continue).",
    )
    args = parser.parse_args()

    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set. See the README.")

    asyncio.run(
        _run(
            args.in_path,
            args.out,
            query_column=args.query_column,
            new_column=args.column,
            concurrency=args.concurrency,
            fail_fast=args.fail_fast,
        )
    )


if __name__ == "__main__":
    main()
