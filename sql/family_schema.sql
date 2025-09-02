-- Family / member / profile schema (idempotent)
-- Author seed: Charles Bowen

CREATE TABLE IF NOT EXISTS families (
  id BIGSERIAL PRIMARY KEY,
  family_key TEXT UNIQUE,
  display_name TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS family_members (
  id BIGSERIAL PRIMARY KEY,
  family_id BIGINT NOT NULL REFERENCES families(id) ON DELETE CASCADE,
  given_name TEXT,
  family_name TEXT,
  full_name TEXT NOT NULL,
  role TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (family_id, full_name)
);

CREATE TABLE IF NOT EXISTS member_profiles (
  member_id BIGINT PRIMARY KEY REFERENCES family_members(id) ON DELETE CASCADE,
  preferences JSONB DEFAULT '{}'::jsonb,
  traits JSONB DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Helpful indexes (IF NOT EXISTS guarded by unique / primary keys for safety)
CREATE INDEX IF NOT EXISTS idx_family_members_family_id ON family_members(family_id);

-- Seed default family & owner member for Charles Bowen (idempotent)
INSERT INTO families (family_key, display_name)
VALUES ('bowen_default', 'Bowen Family')
ON CONFLICT (family_key) DO NOTHING;

INSERT INTO family_members (family_id, given_name, family_name, full_name, role)
SELECT f.id, 'Charles', 'Bowen', 'Charles Bowen', 'owner'
FROM families f
WHERE f.family_key = 'bowen_default'
  AND NOT EXISTS (
    SELECT 1 FROM family_members m WHERE m.family_id = f.id AND m.full_name = 'Charles Bowen'
  );
