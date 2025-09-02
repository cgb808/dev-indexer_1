-- Conversation / Timeline Schema (idempotent)
-- Hypertables created only if timescaledb present

CREATE EXTENSION IF NOT EXISTS pgcrypto; -- for gen_random_uuid if available

CREATE TABLE IF NOT EXISTS conversation_sessions (
  id BIGSERIAL PRIMARY KEY,
  session_id UUID DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  started_at TIMESTAMPTZ DEFAULT now(),
  ended_at TIMESTAMPTZ,
  metadata JSONB
);
CREATE UNIQUE INDEX IF NOT EXISTS conversation_sessions_session_id_idx ON conversation_sessions(session_id);
CREATE INDEX IF NOT EXISTS conversation_sessions_user_idx ON conversation_sessions(user_id, started_at DESC);

CREATE TABLE IF NOT EXISTS conversation_events (
  time TIMESTAMPTZ NOT NULL,
  id BIGSERIAL,
  session_id UUID NOT NULL,
  user_id TEXT NOT NULL,
  role TEXT NOT NULL, -- user | assistant | system
  seq INT,
  content TEXT NOT NULL,
  embedding vector(768),
  embedded BOOLEAN DEFAULT FALSE,
  content_hash TEXT,
  importance SMALLINT,
  retention_policy TEXT, -- ephemeral | candidate | persistent
  metadata JSONB,
  PRIMARY KEY (time, id)
);

CREATE TABLE IF NOT EXISTS conversation_summaries (
  time TIMESTAMPTZ NOT NULL,
  id BIGSERIAL,
  user_id TEXT NOT NULL,
  scope TEXT NOT NULL, -- session | daily | weekly
  summary TEXT NOT NULL,
  embedding vector(768),
  embedded BOOLEAN DEFAULT TRUE,
  importance SMALLINT,
  metadata JSONB,
  PRIMARY KEY (time, id)
);

CREATE TABLE IF NOT EXISTS profile_snapshots (
  time TIMESTAMPTZ NOT NULL,
  user_id TEXT NOT NULL,
  version INT NOT NULL,
  profile JSONB NOT NULL,
  embedding vector(768),
  PRIMARY KEY (time, user_id, version)
);

-- Optional mentions index table (for cross-user references)
CREATE TABLE IF NOT EXISTS mentions_index (
  time TIMESTAMPTZ NOT NULL,
  event_id BIGINT,
  mentioned_user TEXT NOT NULL,
  source_user TEXT NOT NULL,
  session_id UUID,
  context_snippet TEXT,
  metadata JSONB,
  PRIMARY KEY (time, event_id, mentioned_user)
);

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname='timescaledb') THEN
    PERFORM create_hypertable('conversation_events','time', if_not_exists=>TRUE);
    PERFORM create_hypertable('conversation_summaries','time', if_not_exists=>TRUE);
    PERFORM create_hypertable('profile_snapshots','time', if_not_exists=>TRUE);
    PERFORM create_hypertable('mentions_index','time', if_not_exists=>TRUE);
  END IF;
END $$;

-- Indexes
CREATE INDEX IF NOT EXISTS conversation_events_user_time_idx ON conversation_events(user_id, time DESC);
CREATE INDEX IF NOT EXISTS conversation_events_session_seq_idx ON conversation_events(session_id, seq);
CREATE INDEX IF NOT EXISTS conversation_events_content_hash_idx ON conversation_events(content_hash);
CREATE INDEX IF NOT EXISTS conversation_summaries_user_time_idx ON conversation_summaries(user_id, time DESC);
CREATE INDEX IF NOT EXISTS mentions_index_mentioned_user_time_idx ON mentions_index(mentioned_user, time DESC);

-- Vector index (ivfflat) for events / summaries (tunable lists)
CREATE INDEX IF NOT EXISTS conversation_events_embedding_ivf ON conversation_events USING ivfflat (embedding vector_l2_ops) WITH (lists=100);
CREATE INDEX IF NOT EXISTS conversation_summaries_embedding_ivf ON conversation_summaries USING ivfflat (embedding vector_l2_ops) WITH (lists=50);
