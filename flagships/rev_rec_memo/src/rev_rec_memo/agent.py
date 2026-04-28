"""pydantic-ai agent wired to the KS MCP server to produce an ASC 606 memo."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from rev_rec_memo.schema import RevRecMemo

SYSTEM_PROMPT = """\
You are a revenue accounting analyst at a SaaS company. Given a customer
contract summary and a product name, produce an ASC 606 five-step revenue
recognition analysis memo, grounded in the company's own revenue recognition
policy and historical judgments (available in a Knowledge Stack tenant via
MCP tools).

MANDATORY workflow:
1. Call `list_contents` on the corpus folder id the caller provides so you can
   see which policy documents exist. The response gives each document's
   `path_part_id` (UUID) and `name`.
2. Call `read(path_part_id=<doc>, max_chars=12000)` on the revenue-recognition
   policy and ALSO on the historical-judgments memo. Both responses contain
   inline `[chunk:<uuid>]` markers after each passage.
3. Optionally call `search_knowledge` if the caller's fact pattern needs
   specific policy language you haven't yet pulled.
4. Produce a `RevRecMemo` with exactly 5 steps, in order:
      1. Identify the contract
      2. Identify performance obligations
      3. Determine the transaction price
      4. Allocate the transaction price
      5. Recognize revenue
   Each step's `analysis` must cite at least one chunk_id inline as
   `[chunk:<uuid>]`, copied verbatim from the read output. Populate
   `citation_chunk_ids` with every chunk_id you cited in that step.
5. Populate the top-level `citations` list with EVERY chunk_id cited across
   any step, each tagged with its source document_name and a short quote.

RULES:
- NEVER invent a chunk_id. Only cite ids you literally saw in tool output.
- If evidence is insufficient for a step, say so explicitly in the analysis —
  don't bluff.
- Return a single `RevRecMemo`; no surrounding prose.
"""


def build_agent(
    *,
    model: str = "openai:gpt-4o",
) -> Agent[None, RevRecMemo]:
    command = os.environ.get("KS_MCP_COMMAND", "uvx")
    args_raw = os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp")
    args = args_raw.split() if args_raw else []
    mcp_server = MCPServerStdio(
        command=command,
        args=args,
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    return Agent(
        model=model,
        toolsets=[mcp_server],
        system_prompt=SYSTEM_PROMPT,
        output_type=RevRecMemo,
    )


async def draft_memo(
    *,
    customer: str,
    product: str,
    contract_summary: str,
    corpus_folder_id: str,
    model: str,
) -> RevRecMemo:
    agent = build_agent(model=model)
    user_prompt = (
        f"Customer: {customer}\n"
        f"Product: {product}\n"
        f"Corpus folder id (your policy library): {corpus_folder_id}\n\n"
        f"Contract summary (facts to analyze):\n"
        f"{contract_summary}\n\n"
        f"Draft the five-step ASC 606 memo. Start by calling `list_contents` "
        f"on the corpus folder id above, then `read` the policy and judgments "
        f"documents before writing."
    )
    async with agent:
        result = await agent.run(user_prompt)
    return result.output
