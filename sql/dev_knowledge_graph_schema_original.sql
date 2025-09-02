-- =============================================================
-- Development Knowledge Graph Schema (Original Style)
--
-- This file reflects the schema version you provided ("corrected version"),
-- with minor safety adjustments:
--  * Corrected TIMESTPTZ -> TIMESTAMPTZ
--  * Wrapped CREATE TYPE in IF NOT EXISTS blocks
--  * Leaves table names (model_registry, query_performance) un-namespaced.
--    NOTE: If the retrieval schema already created tables with these names,
--    applying this file may error or conflict. Review before executing in a
--    shared database. Use the previously added dev_knowledge_graph_schema.sql
--    for a collision-safe variant.
-- =============================================================

-- 1. EXTENSIONS & CUSTOM TYPES ---------------------------------
CREATE EXTENSION IF NOT EXISTS vector;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='dev_event_type') THEN
    CREATE TYPE dev_event_type AS ENUM (
      'ai_interaction',
      'human_commit',
      'decision_log',
      'bug_report',
      'performance_test'
    );
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='event_outcome') THEN
    CREATE TYPE event_outcome AS ENUM ('win', 'loss', 'neutral', 'observation');
  END IF;
END $$;

-- 2. THE MISSION ------------------------------------------------
CREATE TABLE IF NOT EXISTS project_missions (
  id          BIGSERIAL PRIMARY KEY,
  name        TEXT UNIQUE NOT NULL,
  description TEXT NOT NULL,
  status      TEXT DEFAULT 'active',
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS project_epics (
  id          BIGSERIAL PRIMARY KEY,
  mission_id  BIGINT REFERENCES project_missions(id),
  name        TEXT NOT NULL,
  description TEXT,
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- 3. THE NARRATIVE ----------------------------------------------
CREATE TABLE IF NOT EXISTS development_log (
  id                BIGSERIAL PRIMARY KEY,
  epic_id           BIGINT REFERENCES project_epics(id),
  event_type        dev_event_type NOT NULL,
  outcome           event_outcome,
  title             TEXT NOT NULL,
  narrative         TEXT NOT NULL,
  narrative_embedding vector(768),
  author            TEXT,
  metadata          JSONB DEFAULT '{}'::jsonb,
  occurred_at       TIMESTAMPTZ DEFAULT now()
);

-- 4. THE CODEBASE -----------------------------------------------
CREATE TABLE IF NOT EXISTS source_documents (
  id               BIGSERIAL PRIMARY KEY,
  file_path        TEXT UNIQUE NOT NULL,
  language         TEXT,
  content_hash     TEXT NOT NULL,
  version          INT NOT NULL DEFAULT 1,
  provenance       JSONB,
  created_at       TIMESTAMPTZ DEFAULT now(),
  last_analyzed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS code_chunks (
  id                 BIGSERIAL PRIMARY KEY,
  document_id        BIGINT REFERENCES source_documents(id) ON DELETE CASCADE,
  chunk_name         TEXT,
  start_line         INT NOT NULL,
  end_line           INT NOT NULL,
  code_content       TEXT NOT NULL,
  checksum           TEXT NOT NULL,
  code_embedding     vector(768),
  analysis_metrics   JSONB DEFAULT '{}'::jsonb
);

-- 5. LINKING TABLES ---------------------------------------------
CREATE TABLE IF NOT EXISTS log_to_chunk_link (
  log_id    BIGINT REFERENCES development_log(id) ON DELETE CASCADE,
  chunk_id  BIGINT REFERENCES code_chunks(id) ON DELETE CASCADE,
  PRIMARY KEY (log_id, chunk_id)
);

-- 6. MLOPS & SYSTEM HEALTH -------------------------------------
CREATE TABLE IF NOT EXISTS model_registry (
  id           BIGSERIAL PRIMARY KEY,
  model_type   TEXT NOT NULL,
  name         TEXT NOT NULL,
  version      TEXT NOT NULL,
  meta         JSONB,
  created_at   TIMESTAMPTZ DEFAULT now(),
  UNIQUE(model_type, name, version)
);

CREATE TABLE IF NOT EXISTS query_performance (
  id              BIGSERIAL PRIMARY KEY,
  query_text      TEXT,
  query_embedding vector(768),
  latency_ms      INT,
  results_count   INT,
  metrics         JSONB,
  occurred_at     TIMESTAMPTZ DEFAULT now()
);

-- 7. INDEXES ----------------------------------------------------
CREATE INDEX IF NOT EXISTS dev_log_epic_idx ON development_log(epic_id);
CREATE INDEX IF NOT EXISTS code_chunks_doc_id_idx ON code_chunks(document_id);

CREATE INDEX IF NOT EXISTS dev_log_embedding_idx
  ON development_log USING ivfflat (narrative_embedding vector_cosine_ops) WITH (lists=100);

CREATE INDEX IF NOT EXISTS code_chunks_embedding_idx
  ON code_chunks USING ivfflat (code_embedding vector_cosine_ops) WITH (lists=100);

-- End dev_knowledge_graph_schema_original.sql
