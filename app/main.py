import os
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

# ---------------------------
# ENV
# ---------------------------
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@vortexai.local")
FROM_NAME = os.getenv("FROM_NAME", "VortexAI")

# ---------------------------
# APP
# ---------------------------
app = FastAPI(title="VortexAI", version="9.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# DB
# ---------------------------
def get_conn():
    return psycopg2.connect(DATABASE_URL)

# ---------------------------
# LEVEL 4: EMAIL (BREVO)
# ---------------------------
def send_email(to_email: str, subject: str, html_content: str):
    if not BREVO_API_KEY:
        print(f"[EMAIL-SKIP] To={to_email} Subject={subject} (BREVO_API_KEY missing)")
        return

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }
    payload = {
        "sender": {"name": FROM_NAME, "email": FROM_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content,
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        if r.status_code >= 300:
            print("Brevo email error:", r.status_code, r.text)
    except Exception as e:
        print("Brevo email exception:", e)

# ---------------------------
# LEVEL 2: AI SCORING
# ---------------------------
def clamp(n, lo=0, hi=100):
    return max(lo, min(hi, int(n)))

def score_deal(deal: dict) -> dict:
    category = (deal.get("category") or "").lower()
    price = float(deal.get("price") or 0)
    desc = (deal.get("description") or "").lower()

    profit = 50
    urgency = 50
    risk = 50

    # category price heuristics
    if category == "cars":
        if price <= 5000:
            profit += 25
        elif price <= 15000:
            profit += 15
        elif price >= 30000:
            profit -= 10

    if category == "business":
        if price <= 100000:
            profit += 20
        elif price >= 500000:
            profit -= 10

    if category == "real_estate":
        if price <= 150000:
            profit += 20
        elif price >= 500000:
            profit -= 10

    hot_words = ["urgent", "must sell", "moving", "foreclosure", "auction", "cashflow", "owner retiring"]
    bad_words = ["salvage", "no title", "scam", "broken", "lawsuit"]

    if any(w in desc for w in hot_words):
        urgency += 25
        profit += 10

    if any(w in desc for w in bad_words):
        risk += 30
        profit -= 15

    ai_score = clamp((profit * 0.45) + (urgency * 0.30) + ((100 - risk) * 0.25))

    return {
        "profit_score": clamp(profit),
        "urgency_score": clamp(urgency),
        "risk_score": clamp(risk),
        "ai_score": ai_score
    }

# ---------------------------
# SUCCESS FEE LOGIC
# ---------------------------
def estimated_fee_for_category(category: str) -> int:
    fee_map = {
        "cars": 500,
        "business": 5000,
        "real_estate": 10000,
    }
    return int(fee_map.get((category or "").lower(), 500))

# ---------------------------
# LEVEL 3: MATCH TO BUYER REQUESTS
# ---------------------------
def match_deal_to_requests(conn, deal_row: dict):
    """
    Returns list of matched buyer emails.
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        select id, buyer_email, keywords, location
        from buyer_requests
        where active=true
          and category=%s
          and min_budget <= %s
          and max_budget >= %s
    """, (
        deal_row["category"],
        deal_row["price"],
        deal_row["price"],
    ))
    reqs = cur.fetchall()

    matched_emails = []

    for r in reqs:
        # match_score: use ai_score for now (simple + effective)
        match_score = int(deal_row.get("ai_score") or 50)

        cur2 = conn.cursor()
        cur2.execute("""
            insert into deal_request_matches(deal_id, request_id, match_score)
            values (%s, %s, %s)
        """, (
            deal_row["id"],
            r["id"],
            match_score
        ))
        cur2.close()

        matched_emails.append(r["buyer_email"])

    conn.commit()
    cur.close()
    return matched_emails

# ---------------------------
# BASIC ROUTES
# ---------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html><body style="font-family:Arial;padding:25px;max-width:900px;margin:auto">
      <h1>VortexAI ✅ Running</h1>
      <ul>
        <li><a href="/buyers/request">Buyer: Request Deal</a></li>
        <li><a href="/sell">Seller: Submit Deal</a></li>
        <li><a href="/dealers/apply">Dealer: Register</a></li>
        <li><a href="/deals">View Deals (JSON)</a></li>
      </ul>
      <p style="color:#666">Tip: Buyer submits request → Worker posts deals → AI scores → matches → emails.</p>
    </body></html>
    """

# ---------------------------
# BUYER REQUEST FORM + API
# ---------------------------
@app.get("/buyers/request", response_class=HTMLResponse)
def buyer_request_form():
    return """
    <html><body style="font-family:Arial;max-width:700px;margin:25px auto">
    <h2>Buyer Request</h2>
    <form id="f">
      <label>Email</label><br/><input name="buyer_email" type="email" required style="width:100%"><br/><br/>
      <label>Category</label><br/>
      <select name="category" style="width:100%">
        <option value="cars">Cars</option>
        <option value="business">Small Business</option>
        <option value="real_estate">Real Estate</option>
      </select><br/><br/>
      <label>Keywords</label><br/><input name="keywords" style="width:100%"><br/><br/>
      <label>Location (optional)</label><br/><input name="location" style="width:100%"><br/><br/>
      <label>Min Budget</label><br/><input name="min_budget" type="number" value="0" style="width:100%"><br/><br/>
      <label>Max Budget</label><br/><input name="max_budget" type="number" value="100000" style="width:100%"><br/><br/>
      <button type="submit">Submit Request</button>
    </form>
    <pre id="out" style="background:#f6f6f6;padding:12px;margin-top:15px;border-radius:8px"></pre>
    <script>
      document.getElementById("f").addEventListener("submit", async (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        const obj = Object.fromEntries(fd.entries());
        obj.min_budget = Number(obj.min_budget);
        obj.max_budget = Number(obj.max_budget);
        const r = await fetch("/api/buyers/request", {
          method:"POST",
          headers: {"Content-Type":"application/json"},
          body: JSON.stringify(obj)
        });
        const j = await r.json();
        document.getElementById("out").textContent = JSON.stringify(j, null, 2);
        e.target.reset();
      });
    </script>
    </body></html>
    """

@app.post("/api/buyers/request")
def create_buyer_request(payload: dict):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            insert into buyer_requests (buyer_email, category, keywords, location, min_budget, max_budget)
            values (%s,%s,%s,%s,%s,%s)
        """, (
            payload["buyer_email"],
            payload["category"],
            payload.get("keywords", ""),
            payload.get("location", ""),
            payload.get("min_budget", 0),
            payload.get("max_budget", 10000000),
        ))
        conn.commit()
        cur.close()

        send_email(
            payload["buyer_email"],
            "VortexAI – Buyer Request Active",
            "<p>Your request is active. We will email you when a matching deal is found.</p>"
        )

        return {"status": "ok"}
    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"status":"error","message":str(e)})
    finally:
        conn.close()

# ---------------------------
# SELLER FORM + API (LEVEL 2–4 RUNS HERE)
# ---------------------------
@app.get("/sell", response_class=HTMLResponse)
def seller_form():
    return """
    <html><body style="font-family:Arial;max-width:700px;margin:25px auto">
    <h2>Seller: Submit Deal</h2>
    <form id="f">
      <label>Your Email</label><br/><input name="email" type="email" style="width:100%"><br/><br/>
      <label>Category</label><br/>
      <select name="category" style="width:100%">
        <option value="cars">Cars</option>
        <option value="business">Small Business</option>
        <option value="real_estate">Real Estate</option>
      </select><br/><br/>
      <label>Location</label><br/><input name="location" style="width:100%" required><br/><br/>
      <label>Price</label><br/><input name="price" type="number" style="width:100%" required><br/><br/>
      <label>Description</label><br/><textarea name="description" style="width:100%" rows="5"></textarea><br/><br/>
      <button type="submit">Submit Deal</button>
    </form>
    <pre id="out" style="background:#f6f6f6;padding:12px;margin-top:15px;border-radius:8px"></pre>
    <script>
      document.getElementById("f").addEventListener("submit", async (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        const obj = Object.fromEntries(fd.entries());
        obj.price = Number(obj.price);
        const r = await fetch("/api/sell", {
          method:"POST",
          headers: {"Content-Type":"application/json"},
          body: JSON.stringify(obj)
        });
        const j = await r.json();
        document.getElementById("out").textContent = JSON.stringify(j, null, 2);
        e.target.reset();
      });
    </script>
    </body></html>
    """

@app.post("/api/sell")
def sell(payload: dict):
    """
    LEVEL 2: score
    save deal
    LEVEL 3: match
    LEVEL 4: email
    """
    # normalize
    category = (payload.get("category") or "").lower().strip()
    location = (payload.get("location") or "").strip()
    price = float(payload.get("price") or 0)
    description = payload.get("description") or ""
    seller_email = payload.get("email") or ""

    if category not in ["cars", "business", "real_estate"]:
        return JSONResponse(status_code=400, content={"status":"error","message":"category must be cars|business|real_estate"})
    if not location or price <= 0:
        return JSONResponse(status_code=400, content={"status":"error","message":"location and price required"})

    deal = {
        "category": category,
        "location": location,
        "price": price,
        "description": description
    }

    # Level 2 scoring
    scores = score_deal(deal)
    deal.update(scores)

    # fee
    deal["estimated_fee"] = estimated_fee_for_category(category)

    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            insert into deals (category, location, price, description, ai_score, profit_score, urgency_score, risk_score, estimated_fee)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            returning *
        """, (
            deal["category"],
            deal["location"],
            deal["price"],
            deal["description"],
            deal["ai_score"],
            deal["profit_score"],
            deal["urgency_score"],
            deal["risk_score"],
            deal["estimated_fee"],
        ))
        deal_row = cur.fetchone()
        conn.commit()
        cur.close()

        # Level 3 matching
        matched_emails = match_deal_to_requests(conn, deal_row)

        # Level 4 emails
        if seller_email:
            send_email(
                seller_email,
                "VortexAI – Deal Submitted",
                "<p>Your deal was received. Our AI is scoring it and matching buyers now.</p>"
            )

        for email in matched_emails:
            send_email(
                email,
                "🔥 New Deal Match Found",
                f"""
                <h3>New {deal_row['category']} deal matched to your request</h3>
                <p><b>Location:</b> {deal_row['location']}</p>
                <p><b>Price:</b> ${deal_row['price']}</p>
                <p><b>AI Score:</b> {deal_row['ai_score']}</p>
                <p><b>Description:</b> {deal_row['description']}</p>
                <p style="color:#666">Reply to this email to claim the deal.</p>
                """
            )

        return {
            "status": "ok",
            "deal_id": str(deal_row["id"]),
            "ai_score": int(deal_row["ai_score"]),
            "estimated_fee": float(deal_row["estimated_fee"]),
            "matched_buyers": len(matched_emails),
        }

    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"status":"error","message":str(e)})
    finally:
        conn.close()

# ---------------------------
# DEALERS (OPTIONAL)
# ---------------------------
@app.get("/dealers/apply", response_class=HTMLResponse)
def dealer_form():
    return """
    <html><body style="font-family:Arial;max-width:700px;margin:25px auto">
    <h2>Dealer Registration</h2>
    <form id="f">
      <label>Company</label><br/><input name="company" style="width:100%" required><br/><br/>
      <label>Email</label><br/><input name="email" type="email" style="width:100%" required><br/><br/>
      <label>Phone</label><br/><input name="phone" style="width:100%"><br/><br/>
      <button type="submit">Register</button>
    </form>
    <pre id="out" style="background:#f6f6f6;padding:12px;margin-top:15px;border-radius:8px"></pre>
    <script>
      document.getElementById("f").addEventListener("submit", async (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        const obj = Object.fromEntries(fd.entries());
        const r = await fetch("/api/dealers/apply", {
          method:"POST",
          headers: {"Content-Type":"application/json"},
          body: JSON.stringify(obj)
        });
        const j = await r.json();
        document.getElementById("out").textContent = JSON.stringify(j, null, 2);
        e.target.reset();
      });
    </script>
    </body></html>
    """

@app.post("/api/dealers/apply")
def create_dealer(payload: dict):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            insert into dealers(company, email, phone)
            values (%s,%s,%s)
        """, (
            payload.get("company",""),
            payload.get("email",""),
            payload.get("phone",""),
        ))
        conn.commit()
        cur.close()
        return {"status": "ok"}
    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"status":"error","message":str(e)})
    finally:
        conn.close()

# ---------------------------
# VIEW DEALS (JSON)
# ---------------------------
@app.get("/deals")
def list_deals(limit: int = 100):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("select * from deals order by created_at desc limit %s", (limit,))
        rows = cur.fetchall()
        cur.close()
        return {"count": len(rows), "deals": rows}
    finally:
        conn.close()
