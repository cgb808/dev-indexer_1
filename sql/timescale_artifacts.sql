-- Artifact & time-context linkage schema
-- Registers MessagePack (or other) ingestion artifacts and links them to rows in doc_embeddings.
-- Provides a time-series friendly hypertable for future conversation / session expansion.

CREATE TABLE IF NOT EXISTS artifact_registry (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT now(),
  artifact_type TEXT NOT NULL, -- e.g. 'rag_msgpack_batch'
  path TEXT NOT NULL,
  sha256 TEXT,
  bytes BIGINT,
  metadata JSONB
);

-- Bridge table linking artifacts to embedding rows
CREATE TABLE IF NOT EXISTS doc_embedding_artifact_map (
  artifact_id BIGINT REFERENCES artifact_registry(id) ON DELETE CASCADE,
  embedding_id BIGINT REFERENCES doc_embeddings(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (artifact_id, embedding_id)
);

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname='timescaledb') THEN
    PERFORM create_hypertable('artifact_registry','created_at', if_not_exists=>TRUE);
    PERFORM create_hypertable('doc_embedding_artifact_map','created_at', if_not_exists=>TRUE);
  END IF;
END $$;

-- Indexes for faster lookups
CREATE INDEX IF NOT EXISTS artifact_registry_type_created_idx ON artifact_registry(artifact_type, created_at);
CREATE INDEX IF NOT EXISTS doc_embedding_artifact_map_embedding_idx ON doc_embedding_artifact_map(embedding_id);
