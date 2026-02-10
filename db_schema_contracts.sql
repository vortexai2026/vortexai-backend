CREATE TABLE IF NOT EXISTS contract_drafts (
  id UUID PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
  contract_type TEXT NOT NULL,
  data JSONB DEFAULT '{}'::jsonb
);
