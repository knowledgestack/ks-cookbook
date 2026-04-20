"""Change management review — given a proposed prod change, list policy gates.

Pain point: Every PR/deploy that touches prod should map to your change-mgmt
policy (peer review, ticket, rollback plan, off-hours window for risky
changes). Engineers forget the gates; reviewers re-derive them each time.

Framework: raw OpenAI chat completions + MCP stdio.
Tools used: list_contents, read.
Output: stdout (markdown checklist).
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from openai import AsyncOpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.mcp_client import call, call_list, ks_mcp_session  # noqa: E402

POLICIES_FOLDER = os.environ.get(
    "POLICIES_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41"
)

SYSTEM = (
    "You are a change-management reviewer. Given a proposed change, output a "
    "markdown checklist of policy gates the change must satisfy. Format each "
    "row as '- [ ] <gate> — <one-line why> [chunk:<uuid>]' where chunk_id is "
    "copied verbatim from the policy text. Mark a gate as required only if "
    "the policy actually requires it for this change's risk level."
)


async def pick_change_policy(session) -> dict:
    listing = await call_list(session, "list_contents", {"folder_id": POLICIES_FOLDER})
    docs = [p for p in listing if isinstance(p, dict) and p.get("part_type") == "DOCUMENT"]
    if not docs:
        sys.exit("Policies folder is empty.")
    for hint in ("change", "release", "deploy", "sdlc"):
        match = next((d for d in docs if hint in d.get("name", "").lower()), None)
        if match:
            return match
    return docs[0]


async def run(change: str, risk: str) -> None:
    client = AsyncOpenAI()
    async with ks_mcp_session() as session:
        policy = await pick_change_policy(session)
        body = await call(
            session, "read",
            {"path_part_id": policy["path_part_id"], "max_chars": 6000},
        )
        resp = await client.chat.completions.create(
            model=os.environ.get("MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": (
                    f"Proposed change: {change}\nRisk level: {risk}\n\n"
                    f"Policy '{policy['name']}':\n{body}"
                )},
            ],
        )
        print(resp.choices[0].message.content)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--change",
                   default="Drop-and-recreate the orders.user_id index in prod Postgres",
                   help="One-paragraph description of the proposed change.")
    p.add_argument("--risk", default="high", choices=["low", "medium", "high"])
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.change, args.risk))


if __name__ == "__main__":
    main()
