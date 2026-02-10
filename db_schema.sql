-- db_schema.sql

CREATE TABLE IF NOT EXISTS deals (
  id UUID PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  source TEXT NOT NULL,
  external_id TEXT,
  asset_type TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  location TEXT,
  url TEXT,
  price NUMERIC,
  currency TEXT DEFAULT 'USD',

  profit_score NUMERIC DEFAULT 0,
  urgency_score NUMERIC DEFAULT 0,
  risk_score NUMERIC DEFAULT 0,
  ai_score NUMERIC DEFAULT 0,

  decision TEXT DEFAULT 'ignore',
  next_action JSONB DEFAULT '{}'::jsonb,
  status TEXT DEFAULT 'new'
);

CREATE UNIQUE INDEX IF NOT EXISTS deals_unique_source_external
ON deals (source, external_id)
WHERE external_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS buyers (
  id UUID PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  phone TEXT,
  location TEXT,
  asset_types TEXT[] DEFAULT ARRAY[]::TEXT[],
  min_price NUMERIC DEFAULT 0,
  max_price NUMERIC DEFAULT 999999999,
  tier TEXT DEFAULT 'free',
  plan TEXT DEFAULT 'free'
);

CREATE TABLE IF NOT EXISTS notifications (
  id UUID PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  channel TEXT NOT NULL,
  target TEXT NOT NULL,
  subject TEXT,
  body TEXT,
  sent BOOLEAN DEFAULT FALSE,
  error TEXT
);

CREATE TABLE IF NOT EXISTS learning_events (
  id UUID PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb
);
