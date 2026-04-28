"""CLI entry for the NERC CIP compliance evidence pack."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from nerc_compliance_evidence.agent import build_evidence_pack
from nerc_compliance_evidence.schema import NERCEvidencePack


def _render_markdown(pack: NERCEvidencePack) -> str:
    lines = [
        f"# NERC {pack.standard_id} {pack.requirement} — Evidence Pack",
        "",
        f"**Requirement:** {pack.requirement_text}",
        "",
    ]
    for i, item in enumerate(pack.evidence_items, 1):
        lines += [
            f"## {i}. {item.control_description}",
            f"*Status: {item.status.value}*",
            "",
            item.evidence_summary,
            "",
            "**Evidence:**",
        ]
        for c in item.citations:
            q = (c.quote or "").replace("\n", " ").strip()[:300]
            lines.append(f"- {c.source_document} [chunk:{c.chunk_id}]: \u201c{q}\u201d")
        lines.append("")

    if pack.gaps:
        lines += ["## Compliance Gaps"]
        lines += [f"- {g}" for g in pack.gaps]
        lines.append("")

    if pack.auditor_notes:
        lines += ["## Auditor Notes", pack.auditor_notes]
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Build a NERC CIP compliance evidence pack."
    )
    p.add_argument(
        "--standard",
        default="CIP-007-6",
        help="NERC CIP standard ID (default: CIP-007-6).",
    )
    p.add_argument(
        "--requirement", default="R2", help="Requirement number (default: R2)."
    )
    p.add_argument(
        "--corpus-folder",
        default=os.environ.get(
            "CORPUS_FOLDER_ID", "df0c7c21-494e-583f-a2a7-ad9d231fbee9"
        ),
    )
    p.add_argument("--model", default=os.environ.get("MODEL", "gpt-4o"))
    p.add_argument("--out", type=Path, default=Path("nerc-evidence.md"))
    args = p.parse_args()

    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY in .env.")

    pack = asyncio.run(
        build_evidence_pack(
            standard=args.standard,
            requirement=args.requirement,
            corpus_folder_id=args.corpus_folder,
            model=args.model,
        )
    )
    args.out.write_text(_render_markdown(pack))
    total_cites = sum(len(e.citations) for e in pack.evidence_items)
    satisfied = sum(1 for e in pack.evidence_items if e.status.value == "SATISFIED")
    print(
        f"Wrote {args.out} — {len(pack.evidence_items)} items, "
        f"{satisfied} satisfied, {len(pack.gaps)} gaps, "
        f"{total_cites} citations."
    )


if __name__ == "__main__":
    main()
