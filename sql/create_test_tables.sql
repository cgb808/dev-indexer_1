-- Create testing copies of core tables for safe experimentation / evaluation.
-- Uses LIKE INCLUDING ALL to copy indexes & defaults; converts to hypertable when TimescaleDB present.

CREATE TABLE IF NOT EXISTS doc_embeddings_test (LIKE doc_embeddings INCLUDING ALL);

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname='timescaledb') THEN
    PERFORM create_hypertable('doc_embeddings_test','created_at', if_not_exists=>TRUE);
  END IF;
END $$;

-- Optional: auxiliary table to log augmentation provenance during experimentation
CREATE TABLE IF NOT EXISTS augmentation_events_test (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT now(),
  base_example_id TEXT,
  variant_id TEXT,
  technique TEXT,
  notes TEXT
);
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname='timescaledb') THEN
    PERFORM create_hypertable('augmentation_events_test','created_at', if_not_exists=>TRUE);
  END IF;
END $$;
