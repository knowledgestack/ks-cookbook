# Knowledge Stack from a custom MCP client

For anything that isn't a major framework — internal Python services, Node.js backends, Go workers, n8n nodes — talk to `knowledgestack-mcp` directly. MCP is a stable protocol (stdio or Streamable HTTP); KS speaks both.

## When to use this page

- You're outside Python (Node, Go, Rust, …).
- You're inside Python but don't want a framework dependency.
- You're embedding KS in a long-running service that already manages its own retries / lifecycle and you don't want a second runtime owning the MCP session.

## Python — minimal stdio client

The cookbook ships a thin helper at [`recipes/_shared/mcp_client.py`](../../../recipes/_shared/mcp_client.py):

```python
from recipes._shared.mcp_client import ks_mcp_session

async with ks_mcp_session() as session:
    hits = await session.call_tool("search_knowledge", {"query": "ASC 606 step 2"})
    body = await session.call_tool("read", {"path_part_id": hits[0]["path_part_id"]})
    print(body)
```

Behind the scenes it uses the official `mcp` Python SDK with `stdio_client(StdioServerParameters(command="uvx", args=["knowledgestack-mcp"], env={...}))`.

### Build one yourself

```python
import asyncio, os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(
        command="uvx",
        args=["knowledgestack-mcp"],
        env={
            "KS_API_KEY": os.environ["KS_API_KEY"],
            "KS_BASE_URL": os.environ.get("KS_BASE_URL", ""),
        },
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print([t.name for t in tools.tools])
            result = await session.call_tool("search_knowledge", {"query": "MFA policy"})
            print(result.content)

asyncio.run(main())
```

Output `tools.tools` will list:

```
search_knowledge, search_keyword, read, read_around, list_contents,
find, get_info, view_chunk_image, get_organization_info, get_current_datetime
```

## Streamable HTTP (any language)

For non-Python runtimes, run KS as an HTTP server:

```bash
uvx knowledgestack-mcp --http --port 8765
# or, expose to a container network:
KS_API_KEY=sk-user-... uvx knowledgestack-mcp --http --host 0.0.0.0 --port 8765
```

Then any MCP HTTP client works.

### Node.js / TypeScript

```ts
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const transport = new StreamableHTTPClientTransport(new URL("http://localhost:8765/mcp"));
const client = new Client({ name: "my-app", version: "1.0.0" }, { capabilities: {} });
await client.connect(transport);

const tools = await client.listTools();
const hits = await client.callTool({ name: "search_knowledge", arguments: { query: "MFA policy" } });
const body = await client.callTool({ name: "read", arguments: { path_part_id: hits.content[0].path_part_id } });
```

### Go, Rust, etc.

The MCP spec is at <https://modelcontextprotocol.io/specification>. Any conforming client connects the same way; the tool names and argument shapes are listed in the [MCP tool reference](../mcp-tools.md).

## Stateless HTTP for serverless / edge

If you don't want a long-lived `uvx` process per worker:

```bash
uvx knowledgestack-mcp --http --stateless --port 8765
```

Each request is independent — fine for AWS Lambda, Cloudflare Workers, or any short-lived runtime. Trade-off: every request pays MCP handshake cost (~tens of ms).

## Citation handling without a framework

The same rule applies whether you have an LLM or not:

```python
# Parse [chunk:<uuid>] markers from read() output yourself.
import re
CHUNK_RE = re.compile(r"\[chunk:([0-9a-f-]{36})\]")

def extract_chunk_ids(read_output: str) -> list[str]:
    return CHUNK_RE.findall(read_output)
```

If you're feeding `read()` output into your own LLM call, build your prompt so the model copies these markers verbatim into its citations field. Then validate post-hoc that every emitted `chunk_id` was in `extract_chunk_ids()`.

## Permission model

`KS_API_KEY` is the only thing that determines what the server returns. Everything below is just transport:

- One key per user → tenant ACLs work as expected.
- One service-account key shared across users → all users see the union; **don't do this** for multi-tenant apps.
- Rotate keys via the KS dashboard; nothing in the MCP server caches them across restarts.

## Gotchas

- **`stdio_client` blocks until `initialize()`.** If your wrapper "hangs," you forgot the initialize handshake.
- **`call_tool` returns `result.content` as a list of content parts.** For text tools (`search_knowledge`, `read`), grab `result.content[0].text`. The cookbook helper does this for you.
- **HTTP mode behind a proxy:** the server uses Server-Sent Events. Disable proxy buffering or you'll see calls hang at "waiting for response."
- **No structured output enforcement.** That's the framework's job. If you're rolling your own, validate the LLM's JSON output yourself with `pydantic.TypeAdapter` or jsonschema.
