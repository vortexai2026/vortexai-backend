import os
import psycopg2
import psycopg2.extras
from typing import Any, Dict, List, Optional, Tuple

DATABASE_URL = os.getenv("DATABASE_URL")

def _get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg2.connect(DATABASE_URL, sslmode="require", cursor_factory=psycopg2.extras.RealDictCursor)

def fetch_one(query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()

def fetch_all(query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()

def execute(query: str, params: Tuple = ()) -> None:
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
    finally:
        conn.close()
