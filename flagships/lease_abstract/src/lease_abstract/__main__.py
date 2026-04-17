"""CLI entry for the lease-abstract demo."""


import argparse
import os
import sys
from pathlib import Path

from lease_abstract.agent import draft_abstract


def _resolve_lease(cli_name: str, lease_file: Path | None) -> str:
    path = lease_file or (
        Path(__file__).resolve().parents[2] / "sample_inputs" / "lease.txt"
    )
    if path.exists():
        first = path.read_text(encoding="utf-8").strip().splitlines()
        if first and first[0].strip():
            return first[0].strip()
    return cli_name


def main() -> None:
    p = argparse.ArgumentParser(description="Produce a one-page cited lease abstract.")
    p.add_argument("--lease", default="retail_lease_pinetree_crossing",
                   help="Name of the lease document inside the corpus folder.")
    p.add_argument("--lease-file", type=Path, default=None,
                   help="File whose first line overrides --lease.")
    p.add_argument("--out", type=Path, default=Path("lease-abstract.md"))
    p.add_argument("--corpus-folder", default=os.environ.get("CORPUS_FOLDER_ID", ""))
    p.add_argument("--model",
                   default=os.environ.get("LEASE_ABSTRACT_MODEL", "gpt-4o"))
    args = p.parse_args()

    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set.")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set.")
    if not args.corpus_folder:
        sys.exit("--corpus-folder (or CORPUS_FOLDER_ID env) is required.")

    lease_name = _resolve_lease(args.lease, args.lease_file)
    abstract = draft_abstract(
        corpus_folder_id=args.corpus_folder,
        target_lease=lease_name, model=args.model,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(abstract, encoding="utf-8")
    cites = abstract.count("[chunk:")
    print(f"Wrote {args.out} — {len(abstract)} chars, {cites} chunk citation(s).")


if __name__ == "__main__":
    main()
