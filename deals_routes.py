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

# ----------------------------
# CREATE DEAL
# ----------------------------
@router.post("/create")
def create_deal(payload: dict):
    title = payload.get("title")
    price = payload.get("price")
    location = payload.get("location")

    if not title:
        raise HTTPException(status_code=400, detail="title required")

    deal_id = str(uuid.uuid4())

    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO deals (id, title, price, location)
            VALUES (%s, %s, %s, %s)
            """,
            (deal_id, title, price, location)
        )
        conn.commit()
        cur.close()
    finally:
        conn.close()

    return {"status": "created", "deal_id": deal_id}

# ----------------------------
# LIST DEALS
# ----------------------------
@router.get("")
def list_deals():
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM deals ORDER BY id DESC LIMIT 50")
        rows = cur.fetchall()
        cur.close()
        return {"count": len(rows), "deals": rows}
    finally:
        conn.close()
