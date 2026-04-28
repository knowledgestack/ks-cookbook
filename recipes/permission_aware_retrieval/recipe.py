"""Two-tier auth demo — same agent code, different user, different answers.

Pain point every enterprise buyer asks about:
  "If my agent queries our knowledge base, how do I stop it from leaking a
   document to a user who wouldn't otherwise have access?"

KS's answer: identity lives in your IdP (Okta/Azure AD/Google); permissions
live in KS. Your developer holds a dev-issued API key per END-USER, and KS
enforces that user's ``PathPermission`` tuple on every retrieval call.

This recipe runs the SAME ReAct agent loop twice — once with Alice's key
(scoped to access + ir policies), once with Bob's (scoped to sdlc + vendor).
Each agent is asked the same question: "Summarise every policy you can see."

If KS enforcement works, Alice and Bob's answers will be different.

Framework: pydantic-ai (swap to any — auth is about the API key, not the framework).

Seed two users + keys first:
    uv run --env-file .env.e2e python seed/seed_cookbook_users.py
"""

import asyncio
import os
import sys

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

POLICIES_FOLDER = os.environ.get("POLICIES_FOLDER_ID", "")
PROMPT = """List every policy visible under the policies folder
KS workflow (do NOT skip):
1. Ask Knowledge Stack specific natural-language questions about the input. Never use folder UUIDs or path_part_id filters in your queries.
2. search_knowledge returns hits. EACH hit is a JSON object with TWO distinct UUIDs: chunk_id (for citation only) and path_part_id (the chunk's path-tree node, used for read). The text field on the hit is empty.
3. To retrieve the chunk content, call read(path_part_id=<hit.path_part_id>). DO NOT pass chunk_id to read — read() returns 404 on chunk_ids. If you see a 404, you used the wrong UUID; switch to path_part_id from the SAME hit. The read() output ends in a [chunk:<uuid>] marker — that uuid is the citation.chunk_id.
4. Build every output field ONLY from chunk text you read. Never invent facts. If the corpus has nothing relevant, mark the field accordingly (e.g. confidence='low' or 'not in corpus — upload data to proceed').
5. Populate every citation with chunk_id (verbatim from the marker), document_name (filename from read() output's metadata or materialized_path), and snippet (verbatim ≤240 chars from the chunk text). NEVER leave document_name or snippet blank.


Output format (STRICT): Your final response is a single JSON object that matches the response schema exactly. Do NOT wrap it in an extra key like {"<ClassName>": ...} or {"result": ...}. Every required string field is a string, not a nested object. Every required nested model is included with all of its required fields populated. Never omit required fields; never add unspecified ones."""

async def query_as(user_label: str, ks_api_key: str) -> str:
    server_cmd = os.environ.get("KS_MCP_COMMAND", ".venv/bin/ks-mcp")
    server_args = (os.environ.get("KS_MCP_ARGS", "") or "").split()
    mcp = MCPServerStdio(
        command=server_cmd,
        args=server_args,
        env={
            "KS_API_KEY": ks_api_key,
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    agent = Agent(
        model=f"openai:{os.environ.get('MODEL', 'gpt-4o')}",
        mcp_servers=[mcp],
    )
    async with agent.run_mcp_servers():
        result = await agent.run(PROMPT)
    return f"\n\n========== Output for {user_label} ==========\n{getattr(result, 'output', None) or getattr(result, 'data', str(result))}\n"


async def main() -> None:
    alice_key = os.environ.get("ALICE_KS_API_KEY", "")
    bob_key = os.environ.get("BOB_KS_API_KEY", "")
    if not alice_key or not bob_key:
        sys.exit(
            "Set ALICE_KS_API_KEY and BOB_KS_API_KEY. "
            "Run `seed/seed_cookbook_users.py` in the ks-backend repo to mint them."
        )
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY required.")

    alice_out, bob_out = await asyncio.gather(
        query_as("Alice (security-team scope: access + ir)", alice_key),
        query_as("Bob   (engineering-team scope: sdlc + vendor)", bob_key),
    )
    print(alice_out)
    print(bob_out)
    print(
        "\n--- If KS permission enforcement worked, the two outputs differ. ---\n"
        "Identity came from the API key (upstream/'IdP'); the filter came from KS."
    )


if __name__ == "__main__":
    asyncio.run(main())
