"""Employee policy Q&A — ask any question; get a cited answer.

Pain point: Employees slack "do we allow BYOD?", "what's our password rotation?",
"what's the incident response number?" — all buried in policy PDFs.

This recipe: question in → cited answer out in <3 seconds for common questions.

Framework: raw MCP + OpenAI (no agent framework — shortest possible code path).
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from openai import AsyncOpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.mcp_client import call, call_list, ks_mcp_session  # noqa: E402

POLICIES_FOLDER = os.environ.get("POLICIES_FOLDER_ID", "")
async def run(question: str) -> None:
    # 1. Enumerate policies and ask the LLM which one is most relevant.
    async with ks_mcp_session() as session:
        listing = await call_list(session, "list_contents", {"folder_id": POLICIES_FOLDER})
        policies = [p for p in listing if isinstance(p, dict) and p.get("part_type") == "DOCUMENT"]
        if not policies:
            sys.exit("No policies found in the configured folder.")

        client = AsyncOpenAI()
        picker = await client.chat.completions.create(
            model=os.environ.get("MODEL", "gpt-4o"),
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n\n"
                        f"Available policies: {[p['name'] for p in policies]}\n"
                        "Reply with ONE policy name from that list, nothing else."
                    ),
                }
            ],
        )
        chosen_name = (picker.choices[0].message.content or "").strip().strip("'\"")
        chosen = next((p for p in policies if p["name"] == chosen_name), policies[0])

        # 2. Read that policy's text (with inline [chunk:...] markers).
        policy_text = await call(
            session,
            "read",
            {"path_part_id": chosen["path_part_id"], "max_chars": 5000},
        )

        # 3. Ask the LLM to answer using ONLY that text, citing chunk_ids.
        answer = await client.chat.completions.create(
            model=os.environ.get("MODEL", "gpt-4o"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Answer the user's question strictly from the supplied policy text. "
                        "End the answer with 'Source: [chunk:<uuid>]' copied from the text. "
                        "If the text doesn't answer the question, say so explicitly."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Question: {question}\n\nPolicy '{chosen['name']}':\n{policy_text}",
                },
            ],
        )
        print(answer.choices[0].message.content)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--question", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.question))


if __name__ == "__main__":
    main()
