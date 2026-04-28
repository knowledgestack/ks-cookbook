"""Audit-defensible HCC / ICD-10 coder CLI."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from openpyxl import Workbook

from hcc_coder.agent import code_chart
from hcc_coder.schema import CoderReport


def _render_xlsx(report: CoderReport, out: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Coder Report"
    ws.append(
        [
            "patient_id",
            "code",
            "description",
            "hcc_category",
            "encounter_date",
            "confidence",
            "supporting_phrase",
            "source_document",
            "chunk_id",
        ]
    )
    for a in report.assignments:
        primary = a.citations[0] if a.citations else None
        ws.append(
            [
                report.patient_id,
                a.code,
                a.description,
                a.hcc_category or "",
                a.encounter_date,
                a.confidence,
                a.supporting_phrase,
                primary.document_name if primary else "",
                primary.chunk_id if primary else "",
            ]
        )
    if report.unsupported_flags:
        ws2 = wb.create_sheet("Unsupported")
        ws2.append(["claim_code", "reason"])
        for f in report.unsupported_flags:
            ws2.append([f.claim_code, f.reason])
    wb.save(out)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Assign HCC / ICD-10 codes with chunk-level audit citations."
    )
    p.add_argument("--patient-id", required=True)
    p.add_argument(
        "--corpus-folder",
        default=os.environ.get(
            "HCC_CORPUS_FOLDER_ID",
            "ab926019-ac7a-579f-bfda-6c52a13c5f41",
        ),
        help="Folder.id of the patient chart corpus in your KS tenant.",
    )
    p.add_argument("--model", default=os.environ.get("MODEL", "gpt-4o"))
    p.add_argument("--out", type=Path, default=Path("hcc-coding-report.xlsx"))
    args = p.parse_args()

    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY in .env.")

    report = asyncio.run(
        code_chart(
            patient_id=args.patient_id,
            corpus_folder_id=args.corpus_folder,
            model=args.model,
        )
    )
    _render_xlsx(report, args.out)
    hcc_count = sum(1 for a in report.assignments if a.hcc_category)
    print(
        f"Wrote {args.out} — patient={report.patient_id} "
        f"codes={len(report.assignments)} hcc_codes={hcc_count} "
        f"unsupported={len(report.unsupported_flags)}"
    )


if __name__ == "__main__":
    main()
