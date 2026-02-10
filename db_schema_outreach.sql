-- db_schema_outreach.sql

CREATE TABLE IF NOT EXISTS outreach_messages (
  id UUID PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),

  deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,

  channel TEXT NOT NULL DEFAULT 'manual',
  target TEXT,

  subject TEXT,
  body TEXT NOT NULL,

  status TEXT NOT NULL DEFAULT 'draft',
  approved_by TEXT,
  approved_at TIMESTAMPTZ,
  sent_at TIMESTAMPTZ,

  error TEXT
);

CREATE INDEX IF NOT EXISTS outreach_messages_deal_idx
ON outreach_messages (deal_id);

CREATE INDEX IF NOT EXISTS outreach_messages_status_idx
ON outreach_messages (status);
