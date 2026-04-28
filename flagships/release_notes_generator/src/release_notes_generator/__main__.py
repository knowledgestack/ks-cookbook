"""Release Notes Generator CLI."""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from release_notes_generator.agent import run_agent


def main() -> None:
    p = argparse.ArgumentParser(
        description="Release tag → customer-facing notes grounded in specs + migration guide."
    )
    p.add_argument("--input", required=True, help="Input text or question.")
    p.add_argument("--corpus-folder", default=os.environ.get("CORPUS_FOLDER_ID", ""))
    p.add_argument("--model", default=os.environ.get("MODEL", "gpt-4o"))
    p.add_argument("--out", type=Path, default=Path("release_notes_generator.md"))
    args = p.parse_args()

    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY in .env.")
    if not args.corpus_folder:
        sys.exit("--corpus-folder or CORPUS_FOLDER_ID env var required.")

    result = asyncio.run(
        run_agent(
            input_text=args.input,
            corpus_folder_id=args.corpus_folder,
            model=args.model,
        )
    )
    args.out.write_text(json.dumps(result.model_dump(), indent=2, default=str))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
