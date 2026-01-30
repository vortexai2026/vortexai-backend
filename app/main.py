import os
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

# -------------------------------------------------
# ENV
# -------------------------------------------------
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@vortexai.local")
FROM_NAME = os.getenv("FROM_NAME", "VortexAI")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

# -------------------------------------------------
# APP
# -------------------------------------------------
app = FastAPI(title="VortexAI", version="8.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# DB
# -------------------------------------------------
def get_conn():
    return psycopg2.connect(DATABASE_URL)

# -------------------------------------------------
# EMAIL (BREVO)
# -------------------------------------------------
def send_email(to_email: str, subject: str, html: str):
    if not BREVO_API_KEY:
        print("[EMAIL SKIPPED]", subject, to_email)
        return

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": BREVO_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "sender": {"email": FROM_EMAIL, "name": FROM_NAME},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html,
    }
    requests.post(url, headers=headers, json=payload, timeout=15)

# -------------------------------------------------
# AI SCORING
# -------------------------------------------------
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

    if any(w in desc for w in ["urgent", "must sell", "moving", "auction"]):
        urgency += 20
        profit += 10

    if any(w in desc for w in ["salvage", "broken", "no title"]):
        risk += 30
        profit -= 15

    ai_score = clamp((profit * 0.45) + (urgency * 0.3) + ((100 - risk) * 0.25))
    return {"ai_score": ai_score}

# -------------------------------------------------
# HOME
# -------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h1>VortexAI ✅ Running</h1>
    <ul>
      <li><a href="/sell">Seller: Submit Deal</a></li>
      <li><a href="/buyers/request">Buyer: Request Deal</a></li>
      <li><a href="/dealers/apply">Dealer: Register</a></li>
      <li><a href="/deals">View Deals</a></li>
    </ul>
    """

@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------------------------------
# BUYER REQUESTS
# -------------------------------------------------
@app.get("/buyers/request", response_class=HTMLResponse)
def buyer_request_form():
    return """
    <h2>Buyer Request</h2>
    <form method="post" action="/api/buyers/request">
      Email <input name="buyer_email"><br/>
      Category <select name="category">
        <option value="cars">Cars</option>
        <option value="business">Business</option>
        <option value="real_estate">Real Estate</option>
      </select><br/>
      Keywords <input name="keywords"><br/>
      Location <input name="location"><br/>
      Min Budget <input name="min_budget" value="0"><br/>
      Max Budget <input name="max_budget" value="100000"><br/>
      <button>Submit</button>
    </form>
    """

@app.post("/api/buyers/request")
def create_buyer_request(payload: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
      insert into buyer_requests
      (buyer_email, category, keywords, location, min_budget, max_budget)
      values (%s,%s,%s,%s,%s,%s)
    """, (
        payload["buyer_email"],
        payload["category"],
        payload.get("keywords",""),
        payload.get("location",""),
        payload.get("min_budget",0),
        payload.get("max_budget",10000000),
    ))
    conn.commit()
    cur.close()
    conn.close()

    send_email(
        payload["buyer_email"],
        "VortexAI – Request Saved",
        "<p>Your request is live. We’ll email you when a deal matches.</p>"
    )
    return {"status":"ok"}

# -------------------------------------------------
# SELLER DEAL SUBMISSION
# -------------------------------------------------
@app.get("/sell", response_class=HTMLResponse)
def seller_form():
    return """
    <h2>Submit Deal</h2>
    <form method="post" action="/api/sell">
      Email <input name="email"><br/>
      Category <select name="category">
        <option value="cars">Cars</option>
        <option value="business">Business</option>
        <option value="real_estate">Real Estate</option>
      </select><br/>
      Location <input name="location"><br/>
      Price <input name="price"><br/>
      Description <textarea name="description"></textarea><br/>
      <button>Submit</button>
    </form>
    """

@app.post("/api/sell")
def sell(payload: dict):
    category = payload["category"]
    scores = score_deal(payload)

    fee_map = {
        "cars": 500,
        "business": 5000,
        "real_estate": 10000
    }
    estimated_fee = fee_map.get(category, 500)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
      insert into deals
      (category, location, price, description, ai_score, estimated_fee)
      values (%s,%s,%s,%s,%s,%s)
      returning id
    """, (
        category,
        payload["location"],
        payload["price"],
        payload.get("description",""),
        scores["ai_score"],
        estimated_fee
    ))
    deal_id = cur.fetchone()[0]
    conn.commit()
    cur.close()

    match_deal_to_requests(conn, deal_id, payload, scores)
    conn.close()

    send_email(
        payload.get("email","seller@unknown.com"),
        "VortexAI – Deal Received",
        "<p>Your deal was received and matched to buyers.</p>"
    )

    return {"status":"ok","deal_id":str(deal_id),"ai_score":scores["ai_score"]}

# -------------------------------------------------
# MATCH DEAL TO BUYER REQUESTS
# -------------------------------------------------
def match_deal_to_requests(conn, deal_id, deal, scores):
    cur = conn.cursor()
    cur.execute("""
      select id, buyer_email
      from buyer_requests
      where active=true
      and category=%s
      and min_budget <= %s
      and max_budget >= %s
    """, (
        deal["category"],
        deal["price"],
        deal["price"]
    ))
    rows = cur.fetchall()

    for r in rows:
        cur.execute("""
          insert into deal_request_matches(deal_id, request_id, match_score)
          values (%s,%s,%s)
        """, (deal_id, r[0], scores["ai_score"]))

        send_email(
            r[1],
            "🔥 New Deal Match",
            f"""
            <h3>New {deal['category']} Deal</h3>
            <p>Location: {deal['location']}</p>
            <p>Price: ${deal['price']}</p>
            <p>AI Score: {scores['ai_score']}</p>
            """
        )
    conn.commit()
    cur.close()

# -------------------------------------------------
# DEALERS
# -------------------------------------------------
@app.get("/dealers/apply", response_class=HTMLResponse)
def dealer_form():
    return """
    <h2>Dealer Registration</h2>
    <form method="post" action="/api/dealers/apply">
      Company <input name="company"><br/>
      Email <input name="email"><br/>
      Phone <input name="phone"><br/>
      <button>Register</button>
    </form>
    """

@app.post("/api/dealers/apply")
def dealer_apply(payload: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
      insert into dealers(company,email,phone)
      values (%s,%s,%s)
    """, (
        payload["company"],
        payload["email"],
        payload.get("phone",""),
    ))
    conn.commit()
    cur.close()
    conn.close()
    return {"status":"ok"}

# -------------------------------------------------
# DEAL LIST
# -------------------------------------------------
@app.get("/deals")
def list_deals():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from deals order by created_at desc")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
