import os
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

router = APIRouter(prefix="/deals", tags=["deals"])

def get_conn():
    return psycopg2.connect(DATABASE_URL)

# -----------------------------
# CREATE DEAL
# -----------------------------
@router.post("/create")
def create_deal(payload: dict):
    title = payload.get("title")
    price = payload.get("price")
    location = payload.get("location")

    if not title or not price or not location:
        raise HTTPException(status_code=400, detail="title, price, location required")

    deal_id = str(uuid.uuid4())

    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO deals (id, title, price, location, ai_score, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            deal_id,
            title,
            price,
            location,
            80,          -- test AI score
            "new"
        ))
        conn.commit()
        cur.close()
    finally:
        conn.close()

    return {"status": "created", "deal_id": deal_id}

# -----------------------------
# LIST DEALS
# -----------------------------
@router.get("/")
def list_deals():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM deals ORDER BY created_at DESC LIMIT 20")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
