CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS deals (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  price NUMERIC DEFAULT 0,
  location TEXT DEFAULT '',
  asset_type TEXT DEFAULT '',
  source TEXT DEFAULT '',
  status TEXT DEFAULT 'new',
  profit_score NUMERIC DEFAULT 0,
  urgency_score NUMERIC DEFAULT 0,
  risk_score NUMERIC DEFAULT 0,
  ai_score NUMERIC DEFAULT 0,
  decision TEXT DEFAULT '',
  next_action TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS buyers (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT DEFAULT '',
  location TEXT DEFAULT '',
  asset_type TEXT DEFAULT '',
  budget NUMERIC DEFAULT 0,
  tier TEXT DEFAULT 'free',
  plan TEXT DEFAULT 'free',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS outcomes (
  id UUID PRIMARY KEY,
  deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
  outcome TEXT NOT NULL,
  notes TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_deals_asset_type ON deals(asset_type);
CREATE INDEX IF NOT EXISTS idx_deals_ai_score ON deals(ai_score);
CREATE INDEX IF NOT EXISTS idx_deals_created_at ON deals(created_at);
