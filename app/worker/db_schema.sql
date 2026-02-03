-- db_schema.sql

CREATE TABLE IF NOT EXISTS deals (
  id UUID PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  source TEXT NOT NULL,
  external_id TEXT,
  asset_type TEXT NOT NULL,        -- real_estate, cars, businesses, etc
  title TEXT NOT NULL,
  description TEXT,
  location TEXT,
  url TEXT,
  price NUMERIC,
  currency TEXT DEFAULT 'USD',

  -- AI fields
  profit_score NUMERIC DEFAULT 0,
  urgency_score NUMERIC DEFAULT 0,
  risk_score NUMERIC DEFAULT 0,
  ai_score NUMERIC DEFAULT 0,

  -- decision/action
  decision TEXT DEFAULT 'ignore',   -- ignore, review, contact_seller, notify_buyers
  next_action JSONB DEFAULT '{}'::jsonb,
  status TEXT DEFAULT 'new'         -- new, contacted, negotiating, under_contract, sold, failed
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
  tier TEXT DEFAULT 'free',         -- free, pro, vip
  plan TEXT DEFAULT 'free'          -- free, pro, vip
);

CREATE TABLE IF NOT EXISTS notifications (
  id UUID PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  channel TEXT NOT NULL,            -- email, sms, webhook
  target TEXT NOT NULL,             -- email address, phone, url
  subject TEXT,
  body TEXT,
  sent BOOLEAN DEFAULT FALSE,
  error TEXT
);

CREATE TABLE IF NOT EXISTS learning_events (
  id UUID PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,         -- contacted, replied, sold, scam, etc
  metadata JSONB DEFAULT '{}'::jsonb
);
