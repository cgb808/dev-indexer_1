-- pgvector IVF flat index (increase lists after higher row counts)
CREATE INDEX IF NOT EXISTS doc_embeddings_embedding_ivf
ON doc_embeddings
USING ivfflat (embedding vector_l2_ops)
WITH (lists=100);

-- Future optional HNSW (uncomment if pgvector build supports it)
-- CREATE INDEX IF NOT EXISTS doc_embeddings_embedding_hnsw
-- ON doc_embeddings
-- USING hnsw (embedding vector_l2_ops)
-- WITH (m=16, ef_construction=64);

-- Expression index to accelerate duplicate detection & hash lookups
CREATE INDEX IF NOT EXISTS doc_embeddings_content_hash_idx
ON doc_embeddings ((metadata->>'content_hash'));

