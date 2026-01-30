-- db_schema.sql
-- Run manually in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS buyers (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    tier TEXT DEFAULT 'free',
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS buyer_requests (
    id SERIAL PRIMARY KEY,
    buyer_email TEXT NOT NULL,
    category TEXT NOT NULL,
    keywords TEXT,
    location TEXT,
    min_budget NUMERIC,
    max_budget NUMERIC,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS deals (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL,
    location TEXT NOT NULL,
    price NUMERIC,
    description TEXT,
    status TEXT DEFAULT 'new',
    created_at TIMESTAMP DEFAULT now()
);
