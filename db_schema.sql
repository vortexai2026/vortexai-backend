CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS deals (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  price NUMERIC,
  location TEXT,
  asset_type TEXT,
  source TEXT,
  status TEXT DEFAULT 'new',
  ai_score NUMERIC DEFAULT 0,
  profit_score NUMERIC DEFAULT 0,
  urgency_score NUMERIC DEFAULT 0,
  risk_score NUMERIC DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS buyers (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  location TEXT,
  asset_type TEXT,
  budget NUMERIC,
  tier TEXT DEFAULT 'free',
  plan TEXT DEFAULT 'free',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS learning_events (
  id UUID PRIMARY KEY,
  deal_id UUID,
  outcome TEXT,
  adjustment NUMERIC,
  created_at TIMESTAMP DEFAULT NOW()
);
