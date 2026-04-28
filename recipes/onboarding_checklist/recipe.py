"""Onboarding checklist — role → cited day-one checklist from policy corpus.

Pain point: HR copy-pastes the same policy bits into a new-hire doc for every
role. This recipe enumerates the policies folder, lets GPT pick the relevant
documents via OpenAI tool-calling, reads them over MCP stdio, and emits a
markdown checklist with inline `[chunk:<uuid>]` citations from `read` output.

Framework: raw OpenAI function-calling against MCP stdio (no agent framework).
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from openai import AsyncOpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.mcp_client import call, call_list, ks_mcp_session  # noqa: E402

POLICIES_FOLDER = os.environ.get("POLICIES_FOLDER_ID", "")
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "pick_policies",
            "description": "Choose up to 4 policy path_part_ids relevant to onboarding the role.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path_part_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                        "maxItems": 4,
                    },
                },
                "required": ["path_part_ids"],
            },
        },
    }
]

SYSTEM = (
    "Produce a markdown onboarding checklist for the given role using ONLY the supplied "
    "policy text. Group items under Day 1 / Week 1 / First 30 days. Each bullet MUST end "
    "with a `[chunk:<uuid>]` tag copied verbatim from the supplied text. Drop any bullet "
    "without a chunk."
)


async def run(role: str) -> None:
    async with ks_mcp_session() as session:
        listing = await call_list(session, "list_contents", {"folder_id": POLICIES_FOLDER})
        policies = [p for p in listing if isinstance(p, dict) and p.get("part_type") == "DOCUMENT"]
        if not policies:
            sys.exit("No policies found in the configured folder.")

        client = AsyncOpenAI()
        model = os.environ.get("MODEL", "gpt-4o")
        pick = await client.chat.completions.create(
            model=model,
            tools=TOOLS,
            tool_choice={"type": "function", "function": {"name": "pick_policies"}},
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Role: {role}\nPolicies (name → path_part_id): "
                        f"{[(p['name'], p['path_part_id']) for p in policies]}\n"
                        "Pick up to 4 path_part_ids most relevant to day-one onboarding."
                    ),
                }
            ],
        )
        chosen = json.loads(pick.choices[0].message.tool_calls[0].function.arguments)[
            "path_part_ids"
        ]
        valid = {p["path_part_id"]: p["name"] for p in policies}

        sections: list[str] = []
        for ppid in (i for i in chosen if i in valid):
            text = await call(session, "read", {"path_part_id": ppid, "max_chars": 3500})
            sections.append(f"## {valid[ppid]}\n\n{text}")

        out = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"Role: {role}\n\nPolicies:\n{chr(10).join(sections)}"},
            ],
        )
        print(out.choices[0].message.content)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--role", required=True, help="e.g. 'Backend Engineer'")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.role))


if __name__ == "__main__":
    main()
