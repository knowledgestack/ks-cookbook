# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportAny=false, reportAttributeAccessIssue=false, reportUnusedCallResult=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportOptionalSubscript=false, reportReturnType=false, reportMissingTypeArgument=false, reportDeprecated=false, reportUnannotatedClassAttribute=false
"""LlamaIndex recipe — framework #6, same auth pattern.

Pain point: LlamaIndex is the default RAG framework for many teams. The usual
pain is wiring a *permission-aware* retriever into it. With KS MCP tools the
retriever is already permission-aware (it enforces the caller's API-key
scope), so the LlamaIndex side is pure plumbing.

Proves the "use any agentic framework and use us" claim — identical grounding
behaviour as the pydantic-ai / LangGraph / Anthropic / OpenAI recipes.

Framework: LlamaIndex (over KS MCP stdio via the shared helper).
Tools: list_contents, read, search_knowledge.
Output: stdout (one cited paragraph).
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.mcp_client import call, ks_mcp_session  # noqa: E402

POLICIES_FOLDER = os.environ.get("POLICIES_FOLDER_ID", "")
async def run(question: str) -> None:
    from llama_index.core import Document, Settings, VectorStoreIndex
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.llms.openai import OpenAI as LlamaOpenAI

    # 1. Pull the corpus through the MCP tool surface — enforced-by-KS.
    docs: list[Document] = []
    async with ks_mcp_session() as session:
        # Search the whole tenant instead of folder enumeration.
        raw = await call(session, "search_knowledge", {"query": question, "limit": 10})
        try:
            hits = json.loads(raw) if isinstance(raw, str) else raw
        except json.JSONDecodeError:
            hits = []
        items = hits if isinstance(hits, list) else (hits.get("hits") or hits.get("results") or [])
        policies = []
        seen = set()
        for h in items:
            ppid = h.get("path_part_id") or h.get("chunk_id")
            if not ppid or ppid in seen:
                continue
            seen.add(ppid)
            name = (h.get("document_name") or "").split("/")[-1] or f"chunk-{str(ppid)[:8]}"
            policies.append({"name": name, "path_part_id": ppid, "part_type": "DOCUMENT"})
        for policy in policies:
            text = await call(
                session,
                "read",
                {"path_part_id": policy["path_part_id"], "max_chars": 8000},
            )
            docs.append(
                Document(
                    text=text,
                    metadata={"name": policy["name"], "path_part_id": policy["path_part_id"]},
                )
            )

    if not docs:
        sys.exit("No policies visible to this API key. Check KS_API_KEY scope.")

    # 2. Hand the (already-permission-filtered) docs to LlamaIndex as normal.
    Settings.llm = LlamaOpenAI(model=os.environ.get("MODEL", "gpt-4o"))
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=60)
    index = VectorStoreIndex.from_documents(docs)

    # 3. Query — LlamaIndex cites its retrieved nodes, which still carry the
    #    KS chunk markers from the source text, so the final answer is
    #    traceable all the way back to the KS chunk_id.
    query_engine = index.as_query_engine(similarity_top_k=3)
    resp = query_engine.query(question)
    sources = [{"name": n.metadata.get("name"), "score": float(n.score), "path_part_id": n.metadata.get("path_part_id")} for n in resp.source_nodes]
    print(json.dumps({"answer": str(resp), "sources": sources}, indent=2))
    return
    for node in resp.source_nodes:
        print(f"  policy={node.metadata.get('name')!r:22s} score={node.score:.3f}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--question", required=True)
    args = p.parse_args()
    if not os.environ.get("KS_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set KS_API_KEY and OPENAI_API_KEY.")
    asyncio.run(run(args.question))


if __name__ == "__main__":
    main()
