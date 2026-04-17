"""Vendor security review — given a vendor name + category, draft a risk memo.

Pain point: Every new vendor kicks off a 3rd-party risk review.  Security
teams want a consistent first draft grounded in the company's vendor-mgmt
policy + breach notification + data-protection requirements.

Framework: raw Anthropic Messages API + MCP stdio (no agent framework).
"""


import argparse
import asyncio
import os
import sys
from pathlib import Path

from anthropic import AsyncAnthropic

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.mcp_client import ks_mcp_session  # noqa: E402

POLICIES_FOLDER = os.environ.get(
    "POLICIES_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41"
)

SYSTEM = (
    "You are a security analyst drafting a first-pass vendor-risk memo. "
    "Use the MCP tools to read the vendor-management (vendor), breach-response (breach), "
    "and data-protection policies from the policies folder. Produce markdown with: "
    "(1) 3-5 risk items each tied to a policy chunk, (2) required mitigations, "
    "(3) a recommendation (approve / conditional / reject). "
    "Every risk item ends with a ``[chunk:<uuid>]`` citation copied from the read output."
)


async def run(vendor: str, category: str) -> None:
    client = AsyncAnthropic()
    async with ks_mcp_session() as session:
        mcp_tools = await session.list_tools()
        anth_tools = [
            {"name": t.name, "description": t.description or "",
             "input_schema": t.inputSchema or {"type": "object", "properties": {}}}
            for t in mcp_tools.tools
        ]
        messages: list[dict] = [{
            "role": "user",
            "content": (
                f"Vendor: {vendor}\nCategory: {category}\n"
                f"Policies folder path_part_id: {POLICIES_FOLDER}"
            ),
        }]
        for _ in range(8):
            resp = await client.messages.create(
                model=os.environ.get("MODEL", "claude-opus-4-6"),
                system=SYSTEM, tools=anth_tools, max_tokens=2000,
                messages=messages,
            )
            if resp.stop_reason == "end_turn":
                for block in resp.content:
                    if getattr(block, "type", None) == "text":
                        print(block.text)
                return
            assistant_blocks: list[dict] = []
            tool_results: list[dict] = []
            for block in resp.content:
                assistant_blocks.append(block.model_dump(exclude_none=True))
                if getattr(block, "type", None) == "tool_use":
                    args = dict(block.input) if block.input else {}
                    result = await session.call_tool(block.name, args)
                    text = (result.content[0].text if result.content else "")
                    tool_results.append({
                        "type": "tool_result", "tool_use_id": block.id,
                        "content": text[:6000],
                        "is_error": result.isError,
                    })
            messages.append({"role": "assistant", "content": assistant_blocks})
            messages.append({"role": "user", "content": tool_results})


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vendor", required=True, help="Vendor name, e.g. 'Stripe'.")
    p.add_argument("--category", default="data processor",
                   help="Vendor category (data processor, infra, SaaS, etc.).")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Set KS_API_KEY and ANTHROPIC_API_KEY.")
    asyncio.run(run(args.vendor, args.category))


if __name__ == "__main__":
    main()
