"""Realtime SDR agent CLI — text by default, voice with ``--voice`` (requires ``[voice]`` extras).

Connects to the OpenAI Realtime API, enumerates KS MCP tools, and exposes
them to the live session as function-call tools. Writes a MEDDIC-scored
``SessionSummary`` to disk when the session ends.
"""

import argparse
import asyncio
import base64
import os
import sys
from pathlib import Path

from openai import AsyncOpenAI

from realtime_voice_sdr.agent import (
    build_summary_agent,
    call_mcp_tool,
    discover_tools,
    instructions_for,
    mcp_session,
)
from realtime_voice_sdr.schema import SessionSummary

SAMPLE_RATE = 24_000  # Realtime API expects pcm16 @ 24kHz mono.


def _render(s: SessionSummary) -> str:
    lines: list[str] = [
        f"# Realtime SDR Session — {s.prospect}",
        "",
        f"**Mode:** {s.mode}   **Turns:** {s.turns}   **Tool calls:** {s.tool_calls}",
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
    lines += ["", "## Open objections"]
    lines += [f"- {o}" for o in s.open_objections] or ["- (none)"]
    return "\n".join(lines)


async def _summarize(
    prospect: str, mode: str, transcript: list[str], tool_calls: int, model: str, out: Path
) -> None:
    summary_agent = build_summary_agent(model=model)
    convo = "\n".join(transcript) or "(empty)"
    result = await summary_agent.run(
        f"Prospect: {prospect}\nMode: {mode}\nTurns: {len(transcript)}\n"
        f"Tool calls: {tool_calls}\n\nTranscript:\n{convo}"
    )
    summary: SessionSummary = (
        getattr(result, "output", None) or getattr(result, "data", None) or result  # type: ignore[assignment]
    )
    out.write_text(_render(summary))
    print(f"\nWrote {out} — next_step={summary.next_step!r}")


async def _run_text(conn, mcp, transcript: list[str], tool_calls: list[int]) -> int:
    """Text REPL over Realtime. Returns number of user turns."""
    turns = 0
    loop = asyncio.get_event_loop()
    print("\nLive SDR session (text over Realtime API). Type '/end' to finish.\n")

    # Prime the bot with an opener.
    await conn.response.create()

    async def consume_until_done() -> None:
        buffer: list[str] = []
        async for event in conn:
            t = event.type
            if t == "response.text.delta" or t == "response.audio_transcript.delta":
                delta = getattr(event, "delta", "") or ""
                print(delta, end="", flush=True)
                buffer.append(delta)
            elif t == "response.function_call_arguments.done":
                name, call_id = event.name, event.call_id
                args = getattr(event, "arguments", "") or ""
                print(f"\n[tool: {name}({args[:80]}{'...' if len(args) > 80 else ''})]")
                tool_calls[0] += 1
                transcript.append(f"[tool: {name}({args[:200]})]")
                result = await call_mcp_tool(mcp, name, args)
                await conn.conversation.item.create(
                    item={
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": result,
                    }
                )
                await conn.response.create()
            elif t == "response.done":
                text = "".join(buffer).strip()
                if text:
                    transcript.append(f"sdr: {text}")
                print()
                return

    await consume_until_done()

    while True:
        try:
            user = await loop.run_in_executor(None, input, "you> ")
        except (EOFError, KeyboardInterrupt):
            break
        if user.strip().lower() in {"/end", "/quit", "/exit"}:
            break
        turns += 1
        transcript.append(f"prospect: {user}")
        await conn.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": user}],
            }
        )
        await conn.response.create()
        await consume_until_done()
    return turns


async def _run_voice(conn, mcp, transcript: list[str], tool_calls: list[int]) -> int:
    """Mic+speaker voice loop over Realtime. Requires the [voice] extras."""
    try:
        import numpy as np
        import sounddevice as sd
    except ImportError:
        sys.exit(
            "Voice mode needs the [voice] extras:\n  uv pip install 'ks-cookbook-voice-sdr[voice]'"
        )

    print("\nLive SDR session (voice). Speak; server VAD commits on pause. Ctrl-C to end.\n")
    q_out: asyncio.Queue[bytes] = asyncio.Queue()

    def mic_cb(indata, _frames, _time, _status) -> None:
        pcm = indata.astype(np.int16).tobytes()
        asyncio.run_coroutine_threadsafe(
            conn.input_audio_buffer.append(audio=base64.b64encode(pcm).decode()),
            asyncio.get_event_loop(),
        )

    def spk_cb(outdata, frames, _time, _status) -> None:
        try:
            chunk = q_out.get_nowait()
        except asyncio.QueueEmpty:
            outdata.fill(0)
            return
        arr = np.frombuffer(chunk, dtype=np.int16)
        n = min(len(arr), frames)
        outdata[:n, 0] = arr[:n]
        if n < frames:
            outdata[n:, 0] = 0

    in_stream = sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="int16", callback=mic_cb, blocksize=2400
    )
    out_stream = sd.OutputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="int16", callback=spk_cb, blocksize=2400
    )

    turns = 0
    with in_stream, out_stream:
        await conn.response.create()
        try:
            async for event in conn:
                t = event.type
                if t == "response.audio.delta":
                    await q_out.put(base64.b64decode(event.delta))
                elif t == "response.audio_transcript.delta":
                    print(getattr(event, "delta", ""), end="", flush=True)
                elif t == "conversation.item.input_audio_transcription.completed":
                    transcript_line = getattr(event, "transcript", "") or ""
                    if transcript_line:
                        turns += 1
                        transcript.append(f"prospect: {transcript_line}")
                elif t == "response.function_call_arguments.done":
                    name, call_id = event.name, event.call_id
                    args = getattr(event, "arguments", "") or ""
                    tool_calls[0] += 1
                    transcript.append(f"[tool: {name}({args[:200]})]")
                    result = await call_mcp_tool(mcp, name, args)
                    await conn.conversation.item.create(
                        item={
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": result,
                        }
                    )
                    await conn.response.create()
                elif t == "response.done":
                    print()
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass
    return turns


async def _run(
    *,
    prospect: str,
    prospect_context: str,
    corpus_folder_id: str,
    realtime_model: str,
    summary_model: str,
    voice: bool,
    out: Path,
) -> None:
    client = AsyncOpenAI()
    transcript: list[str] = []
    tool_calls = [0]

    async with mcp_session() as mcp:
        tools = await discover_tools(mcp)
        instructions = instructions_for(corpus_folder_id, prospect_context)

        async with client.beta.realtime.connect(model=realtime_model) as conn:
            session_config: dict = {
                "instructions": instructions,
                "tools": tools,
                "tool_choice": "auto",
            }
            if voice:
                session_config.update(
                    {
                        "modalities": ["audio", "text"],
                        "voice": "alloy",
                        "input_audio_format": "pcm16",
                        "output_audio_format": "pcm16",
                        "turn_detection": {"type": "server_vad"},
                        "input_audio_transcription": {"model": "whisper-1"},
                    }
                )
            else:
                session_config["modalities"] = ["text"]
            await conn.session.update(session=session_config)

            runner = _run_voice if voice else _run_text
            turns = await runner(conn, mcp, transcript, tool_calls)

    await _summarize(
        prospect=prospect,
        mode="voice" if voice else "text",
        transcript=transcript or [f"prospect: (no turns, {turns} count)"],
        tool_calls=tool_calls[0],
        model=summary_model,
        out=out,
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prospect", required=True)
    p.add_argument("--prospect-context", default="")
    p.add_argument(
        "--corpus-folder",
        default=os.environ.get(
            "SALES_CORPUS_FOLDER_ID",
            "ab926019-ac7a-579f-bfda-6c52a13c5f41",
        ),
    )
    p.add_argument(
        "--realtime-model",
        default=os.environ.get(
            "REALTIME_MODEL",
            "gpt-4o-realtime-preview",
        ),
    )
    p.add_argument("--summary-model", default=os.environ.get("MODEL", "gpt-4o"))
    p.add_argument(
        "--voice", action="store_true", help="Enable mic+speaker audio (needs [voice] extras)."
    )
    p.add_argument("--out", type=Path, default=Path("voice-sdr-session.md"))
    args = p.parse_args()

    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY in .env.")

    asyncio.run(
        _run(
            prospect=args.prospect,
            prospect_context=args.prospect_context,
            corpus_folder_id=args.corpus_folder,
            realtime_model=args.realtime_model,
            summary_model=args.summary_model,
            voice=args.voice,
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
