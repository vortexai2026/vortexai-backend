import os
import uuid
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

# =====================================================
# ENV
# =====================================================
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@vortexai.local")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

# =====================================================
# APP
# =====================================================
app = FastAPI(title="VortexAI", version="FINAL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# DB
# =====================================================
def get_conn():
    return psycopg2.connect(DATABASE_URL)

# =====================================================
# EMAIL (BREVO)
# =====================================================
def send_email(to_email: str, subject: str, html: str):
    if not BREVO_API_KEY:
        print("[EMAIL MOCK]", to_email, subject)
        return

    try:
        r = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": BREVO_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "sender": {"email": FROM_EMAIL},
                "to": [{"email": to_email}],
                "subject": subject,
                "htmlContent": html
            },
            timeout=15
        )
        if r.status_code >= 300:
            print("[BREVO ERROR]", r.status_code, r.text)
    except Exception as e:
        print("[BREVO EXCEPTION]", str(e))

# =====================================================
# HEALTH
# =====================================================
@app.get("/health")
def health():
    return {"status": "ok"}

# =====================================================
# HOME
# =====================================================
@app.get("/", response_class=HTMLResponse)
def home():
    return "<h2>VortexAI ✅ Running</h2>"

# =====================================================
# CREATE DEAL
# =====================================================
@app.post("/api/deals/create")
def create_deal(payload: dict):
    deal_id = str(uuid.uuid4())

    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO deals (
                id,
                title,
                price,
                location,
                category,
                asset_type,
                ai_score,
                estimated_fee,
                status,
                paid
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'new',false)
        """, (
            deal_id,
            payload.get("title"),
            payload.get("price"),
            payload.get("location"),
            payload.get("category"),
            payload.get("asset_type"),
            payload.get("ai_score", 50),
            payload.get("estimated_fee", 0),
        ))
        conn.commit()
        cur.close()

        return {"status": "ok", "deal_id": deal_id}

    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        conn.close()

# =====================================================
# MATCH DEAL → PAID BUYERS
# =====================================================
@app.post("/api/deals/match/{deal_id}")
def match_deal(deal_id: str):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM deals WHERE id=%s", (deal_id,))
        deal = cur.fetchone()
        if not deal:
            cur.close()
            return JSONResponse(status_code=404, content={"error": "Deal not found"})

        cur.execute("""
            SELECT id, email
            FROM buyers
            WHERE tier = 'paid'
              AND asset_type = %s
              AND location ILIKE %s
        """, (
            deal.get("asset_type"),
            f"%{deal.get('location')}%"
        ))

        buyers = cur.fetchall()

        for b in buyers:
            cur.execute("""
                INSERT INTO deal_matches
                (id, deal_id, buyer_id, match_score, status)
                VALUES (%s,%s,%s,%s,'matched')
            """, (
                str(uuid.uuid4()),
                deal_id,
                b["id"],
                int(deal.get("ai_score") or 50)
            ))

            send_email(
                b["email"],
                "🔥 New Deal Matched",
                f"""
                <h3>{deal.get('title')}</h3>
                <p>Location: {deal.get('location')}</p>
                <p>Price: {deal.get('price')}</p>
                <p>AI Score: {deal.get('ai_score')}</p>
                """
            )

        conn.commit()
        cur.close()

        return {"matched_buyers": len(buyers)}

    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        conn.close()

# =====================================================
# VIEW DEALS
# =====================================================
@app.get("/api/deals")
def list_deals(limit: int = 50):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM deals ORDER BY created_at DESC LIMIT %s", (limit,))
        rows = cur.fetchall()
        cur.close()
        return {"count": len(rows), "deals": rows}
    finally:
        conn.close()

# =====================================================
# STRIPE ROUTES
# =====================================================
from stripe_routes import router as stripe_routes
from stripe_webhook import router as stripe_webhook

app.include_router(stripe_routes)
app.include_router(stripe_webhook)
