import os
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
FROM_NAME = os.getenv("FROM_NAME", "VortexAI")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

# =====================================================
# APP
# =====================================================
app = FastAPI(title="VortexAI", version="10.0")

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
        print("[EMAIL SKIPPED] BREVO_API_KEY missing")
        return

    requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "api-key": BREVO_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "sender": {"name": FROM_NAME, "email": FROM_EMAIL},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html
        },
        timeout=15
    )

# =====================================================
# SIMPLE AI SCORING
# =====================================================
def score_deal(category: str, price: float, description: str) -> int:
    score = 50

    if category == "cars":
        if price < 5000: score += 20
        if price > 30000: score -= 10

    if category == "business":
        if price < 100000: score += 20
        if price > 500000: score -= 10

    if category == "real_estate":
        if price < 200000: score += 20
        if price > 600000: score -= 10

    hot = ["urgent", "must sell", "moving", "auction", "cash"]
    bad = ["scam", "broken", "lawsuit", "salvage"]

    desc = description.lower()
    if any(w in desc for w in hot): score += 15
    if any(w in desc for w in bad): score -= 20

    return max(0, min(100, score))

# =====================================================
# MATCH DEAL → BUYER REQUESTS
# =====================================================
def match_deal(conn, deal):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT buyer_email
        FROM buyer_requests
        WHERE active = true
          AND category = %s
          AND min_budget <= %s
          AND max_budget >= %s
    """, (deal["category"], deal["price"], deal["price"]))

    emails = [r["buyer_email"] for r in cur.fetchall()]
    cur.close()
    return emails

# =====================================================
# ROUTES
# =====================================================
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h2>VortexAI ✅ Running</h2>"

# =====================================================
# BUYER REQUEST
# =====================================================
@app.post("/api/buyers/request")
def buyer_request(payload: dict):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO buyer_requests
            (buyer_email, category, keywords, location, min_budget, max_budget, active)
            VALUES (%s,%s,%s,%s,%s,%s,true)
        """, (
            payload["buyer_email"],
            payload["category"],
            payload.get("keywords",""),
            payload.get("location",""),
            payload.get("min_budget",0),
            payload.get("max_budget",10_000_000),
        ))
        conn.commit()
        cur.close()

        send_email(
            payload["buyer_email"],
            "VortexAI – Request Active",
            "<p>Your buyer request is live.</p>"
        )

        return {"status": "ok"}

    except Exception as e:
        conn.rollback()
        return JSONResponse(500, {"error": str(e)})
    finally:
        conn.close()

# =====================================================
# SELL DEAL (CORE FLOW)
# =====================================================
@app.post("/api/sell")
def sell(payload: dict):
    category = payload.get("category","").lower()
    location = payload.get("location","").strip()
    price = float(payload.get("price",0))
    description = payload.get("description","")
    seller_email = payload.get("email","")

    if category not in ["cars","business","real_estate"]:
        return JSONResponse(400, {"error":"Invalid category"})
    if not location or price <= 0:
        return JSONResponse(400, {"error":"Invalid data"})

    ai_score = score_deal(category, price, description)

    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            INSERT INTO deals (category, location, price, description, status)
            VALUES (%s,%s,%s,%s,'new')
            RETURNING *
        """, (category, location, price, description))

        deal = cur.fetchone()
        conn.commit()
        cur.close()

        matched_emails = match_deal(conn, deal)

        if seller_email:
            send_email(
                seller_email,
                "VortexAI – Deal Received",
                "<p>Your deal has been submitted.</p>"
            )

        for email in matched_emails:
            send_email(
                email,
                "🔥 New Deal Match",
                f"""
                <h3>New {category} deal</h3>
                <p>Location: {location}</p>
                <p>Price: ${price}</p>
                <p>AI Score: {ai_score}</p>
                """
            )

        return {
            "status": "ok",
            "deal_id": deal["id"],
            "ai_score": ai_score,
            "matched_buyers": len(matched_emails)
        }

    except Exception as e:
        conn.rollback()
        return JSONResponse(500, {"error": str(e)})
    finally:
        conn.close()

# =====================================================
# VIEW DEALS
# =====================================================
@app.get("/deals")
def view_deals(limit: int = 50):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM deals ORDER BY created_at DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"count": len(rows), "deals": rows}
