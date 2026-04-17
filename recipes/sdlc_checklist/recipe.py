"""Pre-merge SDLC checklist — given a PR description, return required steps.

Pain point: Every engineer needs to remember threat-model review, data-class
check, licence scan, etc. for certain PR kinds. This recipe reads the SDLC
policy and emits the PR-specific checklist with citations.

Framework: LangGraph + MCP adapters (showcases yet another framework).
"""


import argparse
import asyncio
import os
import sys

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

POLICIES_FOLDER = os.environ.get(
    "POLICIES_FOLDER_ID", "ab926019-ac7a-579f-bfda-6c52a13c5f41"
)

SYSTEM = (
    "You are a tech-lead gatekeeper. Given a pull-request description, read the "
    "company's SDLC and data-protection policies from the MCP tools "
    f"(folder path_part_id={POLICIES_FOLDER}) and return a markdown checklist "
    "of pre-merge actions required for this PR. Each item ends with a "
    "``[chunk:<uuid>]`` citation copied from the policy text."
)


async def run(pr: str) -> None:
    cmd = os.environ.get("KS_MCP_COMMAND", "uvx")
    args = (os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split()
    client = MultiServerMCPClient({
        "knowledgestack": {
            "command": cmd, "args": args, "transport": "stdio",
            "env": {
                "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
                "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
            },
        },
    })
    tools = await client.get_tools()
    model = ChatOpenAI(model=os.environ.get("MODEL", "gpt-4o-mini"), max_tokens=1200)
    agent = create_react_agent(model, tools)

    result = await agent.ainvoke({
        "messages": [("system", SYSTEM), ("user", f"PR description:\n{pr}")],
    })
    messages = result.get("messages", [])
    text = messages[-1].content if messages else ""
    if isinstance(text, list):
        text = " ".join(p.get("text", "") for p in text if isinstance(p, dict))
    print(text)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pr", required=True, help="PR description (markdown or plain).")
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.pr))


if __name__ == "__main__":
    main()
