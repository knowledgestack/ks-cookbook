"""CLI entry for the compliance-questionnaire demo."""


import argparse
import asyncio
import os
import sys
from pathlib import Path

from compliance_questionnaire.agent import _build_model, _build_tools, answer_one
from compliance_questionnaire.workbook import load_questions, write_answers


def _format_description(parsed: dict) -> str:
    description = parsed.get("description", "")
    citations = parsed.get("citations", [])
    if not citations:
        return f"{description}\n[Confidence: {parsed.get('confidence', 'LOW')}]"
    cite_lines = "\n".join(
        f"  - {c.get('document_name')} (chunk:{c.get('chunk_id')}): "
        f"\u201c{(c.get('snippet') or '').strip()[:200]}\u201d"
        for c in citations
    )
    return (
        f"{description}\n"
        f"[Confidence: {parsed.get('confidence', 'LOW')}]\n"
        f"Evidence:\n{cite_lines}"
    )


async def _run(
    in_path: Path, out_path: Path, *, policies_folder_id: str, limit: int, concurrency: int,
) -> tuple[int, int]:
    questions = load_questions(in_path, limit=limit)
    if not questions:
        sys.exit(f"No questions found in {in_path}")

    tools = await _build_tools()
    model = _build_model()

    sem = asyncio.Semaphore(concurrency)

    async def _one(q):
        async with sem:
            try:
                parsed = await answer_one(
                    control_id=q.control_id, question=q.question,
                    policies_folder_id=policies_folder_id,
                    tools=tools, model=model,
                )
                return q.row, parsed.get("answer", "INSUFFICIENT EVIDENCE"), _format_description(parsed)
            except Exception as e:  # noqa: BLE001
                return q.row, "ERROR", f"ERROR: {type(e).__name__}: {e}"

    results = await asyncio.gather(*[_one(q) for q in questions])
    answers: dict[int, tuple[str, str]] = {row: (a, d) for row, a, d in results}
    errors = sum(1 for _, a, _ in results if a in ("ERROR", "INSUFFICIENT EVIDENCE"))

    write_answers(in_path, out_path, answers)
    return len(questions), errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-fill a CAIQ/SIG questionnaire from your KS tenant.")
    parser.add_argument("--in", dest="in_path", type=Path, required=True, help="Input XLSX (CAIQv4-format).")
    parser.add_argument("--out", type=Path, required=True, help="Filled XLSX to write.")
    parser.add_argument(
        "--policies-folder",
        default=os.environ.get("POLICIES_FOLDER_ID", ""),
        help="path_part_id of the folder containing policy docs in your KS tenant.",
    )
    parser.add_argument("--limit", type=int, default=5, help="How many rows to answer (default 5).")
    parser.add_argument("--concurrency", type=int, default=3, help="Max concurrent questions.")
    args = parser.parse_args()

    if not os.environ.get("KS_API_KEY"):
        sys.exit("KS_API_KEY is not set. See the README.")
    if not args.policies_folder:
        sys.exit(
            "--policies-folder (or POLICIES_FOLDER_ID env var) is required. "
            "Run `make demo-compliance-setup` to print the folder id for the sample corpus."
        )

    n, err = asyncio.run(_run(
        args.in_path, args.out,
        policies_folder_id=args.policies_folder,
        limit=args.limit, concurrency=args.concurrency,
    ))
    print(f"Filled {n} rows — {err} needed human review. Output: {args.out}")


if __name__ == "__main__":
    main()
