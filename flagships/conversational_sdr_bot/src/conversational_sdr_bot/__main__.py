"""Interactive SDR discovery bot CLI.

Launches a live chat in the terminal. Type ``/end`` to close the session;
the bot then produces a cited MEDDIC-scored summary artifact.
"""


import argparse
import asyncio
import os
import sys
from pathlib import Path

from conversational_sdr_bot.agent import build_summary_agent, build_turn_agent
from conversational_sdr_bot.schema import SessionSummary


def _render(s: SessionSummary) -> str:
    lines: list[str] = [
        f"# SDR Session — {s.prospect}",
        "",
        f"**Turns:** {s.turns}",
        f"**Next step:** {s.next_step}",
        "",
        "## MEDDIC scorecard",
        f"- Metrics: **{s.meddic.metrics}**",
        f"- Economic buyer: **{s.meddic.economic_buyer}**",
        f"- Decision criteria: **{s.meddic.decision_criteria}**",
        f"- Decision process: **{s.meddic.decision_process}**",
        f"- Identify pain: **{s.meddic.identify_pain}**",
        f"- Champion: **{s.meddic.champion}**",
        "",
        "## Discovered pains",
    ]
    lines += [f"- {p}" for p in s.discovered_pains] or ["- (none)"]
    lines += ["", "## Discovered metrics"]
    lines += [f"- {m}" for m in s.discovered_metrics] or ["- (none)"]
    lines += ["", "## Open objections"]
    lines += [f"- {o}" for o in s.open_objections] or ["- (none)"]
    if s.citations_referenced:
        lines += ["", "## Citations referenced"]
        for c in s.citations_referenced:
            snippet = (c.snippet or "").replace("\n", " ").strip()[:240]
            lines.append(f"- *{c.document_name}* (chunk:{c.chunk_id}): \u201c{snippet}\u201d")
    return "\n".join(lines)


async def _run(
    *, prospect: str, prospect_context: str, corpus_folder_id: str, model: str, out: Path,
) -> None:
    turn_agent = build_turn_agent(
        corpus_folder_id=corpus_folder_id, prospect_context=prospect_context, model=model,
    )
    transcript: list[str] = []
    history: list = []

    print(f"\nLive SDR session with {prospect}. Type '/end' to finish.\n")
    async with turn_agent.run_mcp_servers():
        opener = await turn_agent.run("Open the call.", message_history=history)
        reply = getattr(opener, "output", None) or getattr(opener, "data", None) or ""
        history = opener.all_messages()
        print(f"sdr> {reply}\n")
        transcript.append(f"sdr: {reply}")

        loop = asyncio.get_event_loop()
        while True:
            try:
                user = await loop.run_in_executor(None, input, "you> ")
            except (EOFError, KeyboardInterrupt):
                break
            if user.strip().lower() in {"/end", "/quit", "/exit"}:
                break
            transcript.append(f"prospect: {user}")
            result = await turn_agent.run(user, message_history=history)
            history = result.all_messages()
            reply = getattr(result, "output", None) or getattr(result, "data", None) or ""
            print(f"\nsdr> {reply}\n")
            transcript.append(f"sdr: {reply}")

    summary_agent = build_summary_agent(model=model)
    convo = "\n".join(transcript)
    result = await summary_agent.run(
        f"Prospect: {prospect}\nTurns: {len(transcript)}\n\nTranscript:\n{convo}"
    )
    summary: SessionSummary = (
        getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[assignment]
    )
    out.write_text(_render(summary))
    print(f"\nWrote {out} — next_step={summary.next_step!r}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prospect", required=True, help="Prospect company name.")
    p.add_argument(
        "--prospect-context", default="",
        help="Freeform context you know about the prospect (title, source, etc.).",
    )
    p.add_argument(
        "--corpus-folder",
        default=os.environ.get(
            "SALES_CORPUS_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41",
        ),
        help="Folder.id of the product/ICP/past-wins corpus in your KS tenant.",
    )
    p.add_argument("--model", default=os.environ.get("MODEL", "gpt-4o"))
    p.add_argument("--out", type=Path, default=Path("sdr-session.md"))
    args = p.parse_args()

    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY in .env.")

    asyncio.run(_run(
        prospect=args.prospect, prospect_context=args.prospect_context,
        corpus_folder_id=args.corpus_folder, model=args.model, out=args.out,
    ))


if __name__ == "__main__":
    main()
