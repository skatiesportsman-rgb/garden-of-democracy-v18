-- Optional Supabase Free PostgreSQL mirror, not required for public GitHub Pages snapshots.
CREATE TABLE IF NOT EXISTS civic_sources (
  source_id TEXT PRIMARY KEY, name TEXT NOT NULL, status TEXT NOT NULL,
  last_success TIMESTAMPTZ, updated_at TIMESTAMPTZ DEFAULT now(), metadata JSONB NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS civic_polls (
  poll_id TEXT PRIMARY KEY, source_id TEXT NOT NULL, state_code TEXT,
  published_at DATE, fieldwork_start DATE, fieldwork_end DATE,
  pollster TEXT, subject TEXT, payload JSONB NOT NULL,
  imported_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS civic_polls_state_date ON civic_polls(state_code,published_at DESC);
CREATE INDEX IF NOT EXISTS civic_polls_payload_gin ON civic_polls USING GIN(payload);
CREATE TABLE IF NOT EXISTS civic_news (
  article_id TEXT PRIMARY KEY, source_id TEXT NOT NULL, publication TEXT,
  url TEXT NOT NULL, payload JSONB NOT NULL, imported_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS ingestion_audit (
  id BIGSERIAL PRIMARY KEY, source_id TEXT NOT NULL, attempted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  status TEXT NOT NULL, new_records INT NOT NULL DEFAULT 0, details JSONB NOT NULL DEFAULT '{}'
);
-- Expose no direct table access publicly. The static site publishes a reviewed JSON subset.
ALTER TABLE civic_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE civic_polls ENABLE ROW LEVEL SECURITY;
ALTER TABLE civic_news ENABLE ROW LEVEL SECURITY;
ALTER TABLE ingestion_audit ENABLE ROW LEVEL SECURITY;
