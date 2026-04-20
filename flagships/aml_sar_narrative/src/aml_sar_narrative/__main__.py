"""SAR narrative drafter CLI."""


import argparse
import asyncio
import os
import sys
from pathlib import Path

from aml_sar_narrative.agent import draft_sar
from aml_sar_narrative.schema import SARNarrative


def _render_markdown(sar: SARNarrative) -> str:
    lines: list[str] = [
        f"# SAR Narrative — Case {sar.case_id}",
        "",
        f"**Subject:** {sar.subject_name}",
        f"**Filing institution:** {sar.filing_institution}",
        "",
        "## Narrative (FinCEN ≤200 words)",
        sar.narrative,
        "",
        "## W / W / W / W / W / H",
        f"- **Who:** {sar.who}",
        f"- **What:** {sar.what}",
        f"- **When:** {sar.when}",
        f"- **Where:** {sar.where}",
        f"- **Why suspicious:** {sar.why_suspicious}",
        f"- **How:** {sar.how}",
        "",
        "## Red flags",
    ]
    for rf in sar.red_flags:
        lines.append(f"- {rf}")
    lines.append("")
    lines.append("## Evidence")
    for c in sar.citations:
        snippet = (c.snippet or "").replace("\n", " ").strip()[:240]
        lines.append(f"- *{c.document_name}* (chunk:{c.chunk_id}): \u201c{snippet}\u201d")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="Draft a FinCEN-format SAR narrative from case evidence.")
    p.add_argument("--case-id", required=True)
    p.add_argument("--subject", default="", help="Subject entity or individual, if known.")
    p.add_argument(
        "--corpus-folder",
        default=os.environ.get(
            "AML_CORPUS_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41",
        ),
        help="Folder.id of the AML case corpus in your KS tenant.",
    )
    p.add_argument("--model", default=os.environ.get("MODEL", "gpt-4o"))
    p.add_argument("--out", type=Path, default=Path("sar-narrative.md"))
    args = p.parse_args()

    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY in .env.")

    sar = asyncio.run(draft_sar(
        case_id=args.case_id, subject_hint=args.subject,
        corpus_folder_id=args.corpus_folder, model=args.model,
    ))
    args.out.write_text(_render_markdown(sar))
    print(
        f"Wrote {args.out} — case={sar.case_id} red_flags={len(sar.red_flags)} "
        f"citations={len(sar.citations)}"
    )


if __name__ == "__main__":
    main()
