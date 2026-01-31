import os
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

router = APIRouter(prefix="/deals", tags=["deals"])

def get_conn():
    return psycopg2.connect(DATABASE_URL)

# -----------------------------
# CREATE DEAL (TEST / MANUAL)
# -----------------------------
@router.post("/create")
def create_deal(payload: dict):
    title = payload.get("title")
    location = payload.get("location")
    price = payload.get("price")
    ai_score = payload.get("ai_score", 50)

    if not title or not location or price is None:
        raise HTTPException(status_code=400, detail="title, location, price required")

    deal_id = str(uuid.uuid4())

    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO deals (id, title, location, price, ai_score, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (deal_id, title, location, price, ai_score, "new")
        )
        conn.commit()
        cur.close()
    finally:
        conn.close()

    return {
        "id": deal_id,
        "status": "created"
    }

# -----------------------------
# GET ALL DEALS
# -----------------------------
@router.get("")
def list_deals():
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM deals ORDER BY created_at DESC")
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()

# -----------------------------
# GET SINGLE DEAL
# -----------------------------
@router.get("/{deal_id}")
def get_deal(deal_id: str):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM deals WHERE id=%s", (deal_id,))
        deal = cur.fetchone()
        cur.close()

        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")

        return deal
    finally:
        conn.close()
