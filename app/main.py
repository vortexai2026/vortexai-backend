from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

app = FastAPI(title="VortexAI", version="6.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

# -------------------
# Health
# -------------------

@app.get("/health")
def health():
    return {"status": "ok", "service": "VortexAI", "version": "6.0"}

@app.get("/")
def home():
    return {"message": "VortexAI backend running"}

# -------------------
# Sellers
# -------------------

@app.post("/sell")
def create_seller(payload: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        insert into sellers(name, phone, asset_type, location, price, description)
        values (%s,%s,%s,%s,%s,%s)
        returning id
    """, (
        payload.get("name"),
        payload.get("phone"),
        payload.get("asset_type"),
        payload.get("location"),
        payload.get("price"),
        payload.get("description"),
    ))
    seller_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok", "seller_id": seller_id}

# -------------------
# Buyers
# -------------------

@app.post("/buyers/apply")
def create_buyer(payload: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        insert into buyers(name, email, phone, asset_types, min_budget, max_budget, location)
        values (%s,%s,%s,%s,%s,%s,%s)
        returning id
    """, (
        payload.get("name"),
        payload.get("email"),
        payload.get("phone"),
        payload.get("asset_types"),
        payload.get("min_budget"),
        payload.get("max_budget"),
        payload.get("location"),
    ))
    buyer_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok", "buyer_id": buyer_id}

# -------------------
# Dealers
# -------------------

@app.post("/dealers/apply")
def create_dealer(payload: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        insert into dealers(company, contact_name, phone, email, deal_types)
        values (%s,%s,%s,%s,%s)
        returning id
    """, (
        payload.get("company"),
        payload.get("contact_name"),
        payload.get("phone"),
        payload.get("email"),
        payload.get("deal_types"),
    ))
    dealer_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok", "dealer_id": dealer_id}

# -------------------
# Deals
# -------------------

@app.post("/deals")
def create_deal(payload: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        insert into deals(title, asset_type, price, location, seller_id, ai_score)
        values (%s,%s,%s,%s,%s,%s)
        returning id
    """, (
        payload.get("title"),
        payload.get("asset_type"),
        payload.get("price"),
        payload.get("location"),
        payload.get("seller_id"),
        payload.get("ai_score", 50),
    ))
    deal_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok", "deal_id": deal_id}

@app.get("/deals")
def list_deals():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from deals order by created_at desc limit 100")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"count": len(rows), "deals": rows}
