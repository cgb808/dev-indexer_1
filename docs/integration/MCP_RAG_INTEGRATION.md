<!-- Relocated from repository root on 2025-08-30 -->
[Back to Docs Index](../../DOCS_INDEX.md) | See also: [Extended Memory+RAG](../MEMORY_RAG_INTEGRATION.md)

# MCP Memory ↔ RAG Integration

Bridge memory JSONL (server-memory) into pgvector for semantic retrieval.

Flow:
1. Memory JSONL append
2. Tail & dedup hash
3. Embed batch
4. Insert vectors (source='memory')
5. Query retrieval merges memory/doc sources

Env:
```
MEMORY_FILE_PATH=/path/memory.jsonl
DATABASE_URL=postgresql://user:pass@localhost:5432/rag
EMBED_ENDPOINT=http://127.0.0.1:8000/model/embed
```

Run bridge:
`python dev-indexer_1/mcp/memory_rag_bridge.py` (continuous) or `--once`.

SQL union example:
```sql
(SELECT chunk, embedding <-> $Q d FROM doc_embeddings WHERE source='memory'
 UNION ALL
 SELECT chunk, embedding <-> $Q d FROM doc_embeddings WHERE source='docs')
 ORDER BY d ASC LIMIT $K;
```

Future: async queue, summarization, PII redaction, TTL cleanup, metrics instrumentation.
