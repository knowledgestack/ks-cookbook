"""pydantic-ai agent for Employee Handbook Q&A."""

import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.usage import UsageLimits

from employee_handbook_qa.schema import HandbookAnswer

SYSTEM = """\
You answer employee questions from the company handbook. Follow these steps EXACTLY:
1. Call `list_contents(folder_id=__FOLDER_ID__)` to see available handbook documents.
2. Pick the ONE document whose name best matches the question.
3. Call `read(path_part_id=<UUID from step 1>, max_chars=4000)` to get that document's text.
4. Answer the question from the text. Cite with [chunk:<uuid>] from the read output.
5. Return the HandbookAnswer immediately. Do NOT call any more tools.
"""


async def run_agent(*, input_text: str, corpus_folder_id: str, model: str) -> HandbookAnswer:
    server_cmd = os.environ.get("KS_MCP_COMMAND", "uvx")
    server_args = (os.environ.get("KS_MCP_ARGS", "knowledgestack-mcp") or "").split()
    mcp = MCPServerStdio(
        command=server_cmd,
        args=server_args,
        env={
            "KS_API_KEY": os.environ.get("KS_API_KEY", ""),
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    agent = Agent(
        model=f"openai:{model}",
        mcp_servers=[mcp],
        system_prompt=SYSTEM.replace("__FOLDER_ID__", corpus_folder_id),
        output_type=HandbookAnswer,
        retries=4,
        output_retries=4,
    )
    memo = None
    try:
        async with agent.run_mcp_servers():
            result = await agent.run(input_text, usage_limits=UsageLimits(request_limit=200))
            memo = getattr(result, "output", None) or getattr(result, "data", None) or result
    except (BaseExceptionGroup, Exception):
        pass
    if memo is None:
        raise RuntimeError("Agent did not produce a result.")
    return memo
