"""CLI entry for the contract-obligation-extractor flagship."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from contract_obligation_extractor.agent import (
    extract_obligations,
    model_id_default,
)
from contract_obligation_extractor.schema import ObligationReport


PREFERRED_ORDER = (
    "Provider",
    "Customer",
    "Mutual",
    "Processor",
    "Controller",
    "Receiving Party",
    "Disclosing Party",
    "Other",
)


def _render_markdown(report: ObligationReport) -> str:
    groups: dict[str, list] = {h: [] for h in PREFERRED_ORDER}
    for o in report.obligations:
        groups.setdefault(o.holder.value, []).append(o)
    # Keep only holders with at least one entry (plus the canonical trio).
    shown = [
        h
        for h in PREFERRED_ORDER
        if h in ("Provider", "Customer", "Mutual") or groups.get(h)
    ]

    counts_summary = "  ".join(f"**{h}:** {len(groups.get(h, []))}" for h in shown)
    lines: list[str] = [
        f"# Obligation Report — {report.document_name}",
        "",
        f"**Total obligations extracted:** {len(report.obligations)}  ",
        counts_summary,
        "",
    ]
    for holder in shown:
        items = groups.get(holder, [])
        lines.append(f"## {holder} ({len(items)})")
        lines.append("")
        if not items:
            lines.append("_None found._")
            lines.append("")
            continue
        for i, o in enumerate(items, 1):
            sec = f" — _{o.section}_" if o.section else ""
            lines.append(f"### {i}. {o.summary}{sec}")
            lines.append("")
            lines.append(f"- **Verb:** `{o.verb}`")
            lines.append(f"- **Citation:** `[chunk:{o.chunk_id}]`")
            lines.append("")
            quoted = o.quote.strip().replace("\n", " ")
            lines.append(f"> {quoted}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract all shall/must/will obligations from a seeded contract."
    )
    parser.add_argument(
        "--corpus-folder",
        default=os.environ.get(
            "CORPUS_FOLDER_ID",
            "5fa0e0af-561c-5e4e-bfa3-2b66d0e40feb",
        ),
        help="folder_id of the contract corpus in your KS tenant.",
    )
    parser.add_argument(
        "--contract-name",
        default=None,
        help="Substring to pick which document to analyze (e.g. 'msa', 'dpa'). "
        "Defaults to the first document in the folder.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("contract-obligations.md"),
        help="Output markdown path (default: contract-obligations.md).",
    )
    parser.add_argument(
        "--model",
        default=model_id_default(),
        help=f"OpenAI model (default: {model_id_default()}).",
    )
    args = parser.parse_args()

    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set.")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set.")

    report = asyncio.run(
        extract_obligations(
            corpus_folder_id=args.corpus_folder,
            contract_name=args.contract_name,
            model=args.model,
        )
    )
    md = _render_markdown(report)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(md)
    print(
        f"Extracted {len(report.obligations)} obligations from "
        f"{report.document_name!r}. Wrote: {args.out}"
    )


if __name__ == "__main__":
    main()
