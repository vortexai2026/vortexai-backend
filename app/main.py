import os
import stripe
import psycopg2
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="VortexAI", version="8.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# ENV
# ---------------------------

DATABASE_URL = os.getenv("DATABASE_URL")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

STRIPE_PRICE_PRO = os.getenv("STRIPE_PRICE_PRO")
STRIPE_PRICE_VIP = os.getenv("STRIPE_PRICE_VIP")
STRIPE_PRICE_ELITE = os.getenv("STRIPE_PRICE_ELITE")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

def get_conn():
    return psycopg2.connect(DATABASE_URL)

# ---------------------------
# AI scoring
# ---------------------------

def clamp(n, lo=0, hi=100):
    return max(lo, min(hi, int(n)))

def score_deal(deal: dict) -> dict:
    price = float(deal.get("price") or 0)
    desc = (deal.get("description") or "").lower()

    profit = 50
    urgency = 50
    risk = 50

    if price <= 5000:
        profit += 25
    elif price <= 20000:
        profit += 15
    elif price >= 200000:
        profit -= 10

    if any(w in desc for w in ["urgent", "must sell", "auction", "liquidation"]):
        urgency += 25
        profit += 10

    if any(w in desc for w in ["salvage", "broken", "no title", "scam"]):
        risk += 30
        profit -= 15

    ai_score = clamp((profit * 0.45) + (urgency * 0.30) + ((100 - risk) * 0.25))

    return {
        "ai_score": ai_score,
        "profit_estimate": max(0, int(price * (ai_score / 200)))
    }

# ---------------------------
# Buyer matching
# ---------------------------

def match_buyers_for_deal(conn, deal: dict):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from buyers")
    buyers = cur.fetchall()
    cur.close()

    matches = []

    for b in buyers:
        if deal["asset_type"].lower() not in (b.get("asset_types") or "").lower():
            continue

        if not (b["min_budget"] <= deal["price"] <= b["max_budget"]):
            continue

        matches.append((str(b["id"]), deal["ai_score"]))

    return matches

def save_matches(conn, deal_id, matches):
    cur = conn.cursor()
    for buyer_id, score in matches:
        cur.execute(
            "insert into deal_matches(deal_id,buyer_id,match_score,status) values(%s,%s,%s,'matched')",
            (deal_id, buyer_id, score)
        )
    cur.close()

# ---------------------------
# Health
# ---------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------------------
# Homepage + payments
# ---------------------------

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html><body style="font-family:Arial;padding:30px;max-width:900px;margin:auto">
    <h1>VortexAI ✅ Running</h1>

    <ul>
      <li><a href="/sell">Seller: Submit Deal</a></li>
      <li><a href="/buyers/apply">Buyer: Register</a></li>
      <li><a href="/dealers/apply">Dealer: Register</a></li>
      <li><a href="/deals">View Deals (JSON)</a></li>
    </ul>

    <h3>Upgrade Plan</h3>

    <form action="/pay/pro" method="get">
      Email: <input name="email" required>
      <button>Pro – $99</button>
    </form><br>

    <form action="/pay/vip" method="get">
      Email: <input name="email" required>
      <button>VIP – $199</button>
    </form><br>

    <form action="/pay/elite" method="get">
      Email: <input name="email" required>
      <button>Elite – $350</button>
    </form>

    <p>After payment your account upgrades automatically.</p>
    </body></html>
    """

# ---------------------------
# Stripe payments
# ---------------------------

def create_checkout(price_id, email):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        customer_email=email,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url="https://vortexai-backend-production.up.railway.app/",
        cancel_url="https://vortexai-backend-production.up.railway.app/",
        metadata={"price_id": price_id}
    )
    return session.url

@app.get("/pay/pro")
def pay_pro(email: str):
    return {"checkout_url": create_checkout(STRIPE_PRICE_PRO, email)}

@app.get("/pay/vip")
def pay_vip(email: str):
    return {"checkout_url": create_checkout(STRIPE_PRICE_VIP, email)}

@app.get("/pay/elite")
def pay_elite(email: str):
    return {"checkout_url": create_checkout(STRIPE_PRICE_ELITE, email)}

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception:
        return {"status": "invalid"}

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_email")
        price_id = session.get("metadata", {}).get("price_id")

        plan = "free"
        if price_id == STRIPE_PRICE_PRO:
            plan = "pro"
        elif price_id == STRIPE_PRICE_VIP:
            plan = "vip"
        elif price_id == STRIPE_PRICE_ELITE:
            plan = "elite"

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("update buyers set plan=%s where email=%s", (plan, email))
        conn.commit()
        cur.close()
        conn.close()

    return {"status": "ok"}

# ---------------------------
# Seller
# ---------------------------

@app.post("/api/sell")
def seller_submit(payload: dict):
    conn = get_conn()
    try:
        cur = conn.cursor()

        cur.execute("""
        insert into sellers(name,phone,asset_type,location,price,description)
        values(%s,%s,%s,%s,%s,%s) returning id
        """, (
            payload["name"], payload.get("phone"), payload["asset_type"],
            payload["location"], payload["price"], payload.get("description")
        ))

        seller_id = cur.fetchone()[0]

        deal = {
            "asset_type": payload["asset_type"],
            "price": payload["price"],
            "location": payload["location"],
            "description": payload.get("description","")
        }

        scores = score_deal(deal)
        deal.update(scores)

        cur.execute("""
        insert into deals(title,asset_type,price,location,seller_id,ai_score)
        values(%s,%s,%s,%s,%s,%s) returning id
        """, (
            f"{deal['asset_type']} in {deal['location']}",
            deal["asset_type"], deal["price"], deal["location"], seller_id, deal["ai_score"]
        ))

        deal_id = cur.fetchone()[0]

        matches = match_buyers_for_deal(conn, deal)
        save_matches(conn, deal_id, matches)

        conn.commit()

        return {"status":"ok","deal_id":str(deal_id),"ai_score":deal["ai_score"],"matches":len(matches)}

    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"error":str(e)})
    finally:
        conn.close()

# ---------------------------
# Buyers
# ---------------------------

@app.post("/api/buyers/apply")
def create_buyer(payload: dict):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
        insert into buyers(name,email,phone,asset_types,min_budget,max_budget,location,plan)
        values(%s,%s,%s,%s,%s,%s,%s,'free') returning id
        """, (
            payload["name"], payload["email"], payload.get("phone"),
            payload.get("asset_types","cars,wholesale,collectibles,equipment"),
            payload.get("min_budget",0), payload.get("max_budget",10000000),
            payload.get("location","")
        ))
        buyer_id = cur.fetchone()[0]
        conn.commit()
        return {"status":"ok","buyer_id":str(buyer_id)}
    finally:
        conn.close()

# ---------------------------
# Deals + Matches (protected)
# ---------------------------

@app.get("/deals")
def list_deals():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from deals order by created_at desc")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/matches/{deal_id}")
def list_matches(deal_id: str, email: str):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("select plan from buyers where email=%s", (email,))
    buyer = cur.fetchone()

    if not buyer or buyer["plan"] not in ["vip","elite"]:
        raise HTTPException(status_code=403, detail="Upgrade required")

    cur.execute("""
    select dm.*, b.name, b.email
    from deal_matches dm
    join buyers b on b.id=dm.buyer_id
    where dm.deal_id=%s
    """, (deal_id,))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
