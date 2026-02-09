# app/database.py
import os
import psycopg2
import psycopg2.extras

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

def get_conn():
    # connect_timeout prevents hanging in Railway
    return psycopg2.connect(DATABASE_URL, connect_timeout=10)

def fetch_all(query, params=()):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()

def fetch_one(query, params=()):
    rows = fetch_all(query, params)
    return rows[0] if rows else None

def execute(query, params=()):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
        conn.commit()  # ✅ FORCE COMMIT (prevents “it ran but nothing saved”)
