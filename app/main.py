import os
import stripe
import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from psycopg2.extras import RealDictCursor

# Optional SendGrid (email)
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except Exception:
    SENDGRID_AVAILABLE = False

load_dotenv()

app = FastAPI(title="VortexAI", version="9.0")

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

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@vortexai.local")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

def get_conn():
    return psycopg2.connect(DATABASE_URL)

# ---------------------------
# Email helper
# ---------------------------
def send_email(to_email: str, subject: str, html_content: str):
    # Safe fallback: if SendGrid not configured, just logs
    if not SENDGRID_API_KEY or not SENDGRID_AVAILABLE:
        print(f"[EMAIL-SKIP] To={to_email} Subject={subject}")
        return

    try:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        print("Email error:", e)

# ---------------------------
# AI scoring (simple & stable)
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

    if any(w in desc for w in ["urgent", "must sell", "auction", "liquidation", "moving"]):
        urgency += 25
        profit += 10

    if any(w in desc for w in ["salvage", "broken", "no title", "scam", "parts only"]):
        risk += 30
        profit -= 15

    ai_score = clamp((profit * 0.45) + (urgency * 0.30) + ((100 - risk) * 0.25))

    return {
        "ai_score": ai_score,
        "profit_estimate": max(0, int(price * (ai_score / 200)))
    }

# ---------------------------
# Category + Success fee logic
# ---------------------------
def category_from_asset(asset_type: str) -> str:
    a = (asset_type or "").lower()
    if a in ["cars", "car", "vehicle", "vehicles"]:
        return "cars"
    if a in ["business", "biz", "small_business"]:
        return "business"
    if a in ["real_estate", "realestate", "house", "property"]:
        return "real_estate"
    # default
    return "cars"

def estimate_success_fee(category: str, price: float) -> dict:
    """
    Your recommended fees:
    cars: $300-$500 typical (we’ll use 400 default)
    business: $3,000-$10,000 (use 2% capped min 3000)
    real_estate: $2,500-$7,500 (use 1% capped min 2500 max 7500)
    """
    c = (category or "cars").lower()
    if c == "cars":
        return {"estimated_fee": 400, "fee_type": "flat", "fee_percent": 0}
    if c == "business":
        # 2% with min 3000 max 10000
        pct = 2.0
        fee = price * (pct / 100.0)
        fee = max(3000, min(10000, fee))
        return {"estimated_fee": int(fee), "fee_type": "percent", "fee_percent": pct}
    if c == "real_estate":
        # 1% with min 2500 max 7500
        pct = 1.0
        fee = price * (pct / 100.0)
        fee = max(2500, min(7500, fee))
        return {"estimated_fee": int(fee), "fee_type": "percent", "fee_percent": pct}
    return {"estimated_fee": 400, "fee_type": "flat", "fee_percent": 0}

# ---------------------------
# Buyer Request Matching
# ---------------------------
def compute_match_score(deal: dict, req: dict) -> int:
    """
    Match score based on:
    - category match (required)
    - budget fit
    - location contains
    - keyword overlap
    """
    score = 60

    # budget
    price = float(deal.get("price") or 0)
    min_b = float(req.get("min_budget") or 0)
    max_b = float(req.get("max_budget") or 10_000_000)
    if min_b <= price <= max_b:
        score += 20
    else:
        score -= 30

    # location
    deal_loc = (deal.get("location") or "").lower()
    req_loc = (req.get("location") or "").lower().strip()
    if req_loc:
        if req_loc in deal_loc:
            score += 10
        else:
            score -= 10

    # keywords
    kw = (req.get("keywords") or "").lower().strip()
    desc = (deal.get("description") or "").lower()
    title = (deal.get("title") or "").lower()
    if kw:
        # simple keyword split
        pieces = [x.strip() for x in kw.replace(",", " ").split() if x.strip()]
        hits = sum(1 for p in pieces if p in desc or p in title)
        score += min(10, hits * 3)

    return clamp(score)

def match_requests_for_deal(conn, deal: dict):
    """
    Finds active buyer requests for the deal's category, then filters by budget/location, scores them.
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "select * from buyer_requests where active=true and category=%s order by created_at desc",
        (deal["category"],)
    )
    reqs = cur.fetchall()
    cur.close()

    matches = []
    for r in reqs:
        score = compute_match_score(deal, r)
        if score >= 60:  # threshold
            matches.append((str(r["id"]), score, r.get("buyer_email")))
    return matches

def save_request_matches(conn, request_matches: list, deal_id: str):
    cur = conn.cursor()
    for request_id, score, _email in request_matches:
        cur.execute(
            """
            insert into request_matches(request_id, deal_id, match_score, status)
            values (%s,%s,%s,'matched')
            on conflict (request_id, deal_id) do nothing
            """,
            (request_id, deal_id, int(score))
        )
    cur.close()

# ---------------------------
# Stripe checkout
# ---------------------------
def create_checkout(price_id: str, email: str) -> str:
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
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

# ---------------------------
# Routes
# ---------------------------
@app.get("/health")
def health():
    return {"status": "ok", "service": "VortexAI", "version": "9.0"}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html><body style="font-family:Arial;padding:25px;max-width:1000px;margin:auto">
      <h1>VortexAI ✅ Running</h1>

      <h3>Portals</h3>
      <ul>
        <li><a href="/sell">Seller: Submit Deal</a></li>
        <li><a href="/buyers/apply">Buyer: Register</a></li>
        <li><a href="/buyers/request">Buyer: Create Request (cars/business/real estate)</a></li>
        <li><a href="/dealers/apply">Dealer: Register</a></li>
        <li><a href="/deals">View Deals (JSON)</a></li>
      </ul>

      <h3>Upgrade Plan</h3>

      <form action="/pay/pro" method="get">
        Email: <input name="email" required>
        <button type="submit">Pro – $99</button>
      </form><br>

      <form action="/pay/vip" method="get">
        Email: <input name="email" required>
        <button type="submit">VIP – $199</button>
      </form><br>

      <form action="/pay/elite" method="get">
        Email: <input name="email" required>
        <button type="submit">Elite – $350</button>
      </form>

      <p style="color:#666">Tip: Requests + Deals will auto-match and email buyers.</p>
    </body></html>
    """

# ---------------------------
# Payments
# ---------------------------
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
    if not STRIPE_WEBHOOK_SECRET or not stripe.api_key:
        return {"status": "ignored"}

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
        try:
            cur = conn.cursor()
            cur.execute("update buyers set plan=%s where email=%s", (plan, email))
            conn.commit()
            cur.close()
        finally:
            conn.close()

    return {"status": "ok"}

# ---------------------------
# Sellers (web form)
# ---------------------------
@app.get("/sell", response_class=HTMLResponse)
def seller_form():
    return """
    <html><body style="font-family:Arial;max-width:700px;margin:25px auto">
    <h2>Seller Portal — Submit a Deal</h2>
    <form id="f">
      <label>Name</label><br/><input name="name" style="width:100%" required><br/><br/>
      <label>Email</label><br/><input name="email" type="email" style="width:100%"><br/><br/>
      <label>Phone</label><br/><input name="phone" style="width:100%"><br/><br/>

      <label>Category</label><br/>
      <select name="category" style="width:100%">
        <option value="cars">cars</option>
        <option value="business">business</option>
        <option value="real_estate">real_estate</option>
      </select><br/><br/>

      <label>Asset Type</label><br/>
      <input name="asset_type" style="width:100%" value="cars"><br/><br/>

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
def seller_submit(payload: dict):
    """
    1) Insert seller
    2) Score deal
    3) Insert deal with category + success fee estimate
    4) Match buyer requests + store request_matches
    5) Email matched buyers
    """
    conn = get_conn()
    try:
        cur = conn.cursor()

        # insert seller
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

        # build deal
        category = (payload.get("category") or category_from_asset(payload.get("asset_type"))).lower()
        deal = {
            "title": f"{category.upper()} deal in {payload.get('location','')}",
            "asset_type": payload.get("asset_type") or category,
            "category": category,
            "price": float(payload.get("price") or 0),
            "location": payload.get("location") or "",
            "description": payload.get("description") or "",
        }

        # score + fee
        deal.update(score_deal(deal))
        deal.update(estimate_success_fee(category, deal["price"]))

        # insert deal
        cur.execute("""
            insert into deals(title, asset_type, category, price, location, seller_id, ai_score,
                             estimated_fee, fee_type, fee_percent)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            returning id
        """, (
            deal["title"],
            deal["asset_type"],
            deal["category"],
            deal["price"],
            deal["location"],
            str(seller_id),
            int(deal["ai_score"]),
            float(deal["estimated_fee"]),
            deal["fee_type"],
            float(deal["fee_percent"]),
        ))
        deal_id = cur.fetchone()[0]
        cur.close()

        # match buyer requests + store matches
        request_matches = match_requests_for_deal(conn, {"id": str(deal_id), **deal})
        save_request_matches(conn, request_matches, str(deal_id))

        conn.commit()

        # emails (buyers)
        emailed = 0
        for req_id, score, buyer_email in request_matches:
            if buyer_email:
                send_email(
                    buyer_email,
                    "VortexAI — New Deal Matched For You",
                    f"""
                    <h3>New Matched Deal</h3>
                    <p><b>Category:</b> {deal['category']}</p>
                    <p><b>Location:</b> {deal['location']}</p>
                    <p><b>Price:</b> ${int(deal['price']):,}</p>
                    <p><b>AI Score:</b> {int(deal['ai_score'])}</p>
                    <p><b>Estimated Success Fee:</b> ${int(deal['estimated_fee']):,}</p>
                    <p>To view matches (VIP/Elite only):</p>
                    <p><a href="https://vortexai-backend-production.up.railway.app/request-matches/{req_id}?email={buyer_email}">
                       View Request Matches</a></p>
                    """
                )
                emailed += 1

        # seller confirmation
        seller_email = payload.get("email")
        if seller_email:
            send_email(
                seller_email,
                "VortexAI — Your deal was received",
                f"""
                <h3>Deal Received</h3>
                <p><b>Category:</b> {deal['category']}</p>
                <p><b>Location:</b> {deal['location']}</p>
                <p><b>Price:</b> ${int(deal['price']):,}</p>
                <p><b>AI Score:</b> {int(deal['ai_score'])}</p>
                <p><b>Estimated success fee:</b> ${int(deal['estimated_fee']):,}</p>
                """
            )

        return {
            "status": "ok",
            "deal_id": str(deal_id),
            "ai_score": int(deal["ai_score"]),
            "profit_estimate": int(deal["profit_estimate"]),
            "category": deal["category"],
            "estimated_fee": float(deal["estimated_fee"]),
            "request_matches": len(request_matches),
            "emails_sent": emailed
        }

    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
    finally:
        conn.close()

# ---------------------------
# Buyers register (web)
# ---------------------------
@app.get("/buyers/apply", response_class=HTMLResponse)
def buyer_form():
    return """
    <html><body style="font-family:Arial;max-width:700px;margin:25px auto">
    <h2>Buyer Registration</h2>
    <form id="f">
      <label>Name</label><br/><input name="name" style="width:100%" required><br/><br/>
      <label>Email</label><br/><input name="email" type="email" style="width:100%" required><br/><br/>
      <label>Phone</label><br/><input name="phone" style="width:100%"><br/><br/>
      <label>Location (optional)</label><br/><input name="location" style="width:100%"><br/><br/>
      <button type="submit">Register</button>
    </form>
    <pre id="out" style="background:#f6f6f6;padding:12px;margin-top:15px;border-radius:8px"></pre>
    <script>
      document.getElementById("f").addEventListener("submit", async (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        const obj = Object.fromEntries(fd.entries());
        const r = await fetch("/api/buyers/apply", {
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

@app.post("/api/buyers/apply")
def create_buyer(payload: dict):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            insert into buyers(name, email, phone, location, plan)
            values (%s,%s,%s,%s,'free')
            on conflict (email) do update set
              name=excluded.name,
              phone=excluded.phone,
              location=excluded.location
            returning id
        """, (
            payload.get("name"),
            payload.get("email"),
            payload.get("phone",""),
            payload.get("location",""),
        ))
        buyer_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return {"status": "ok", "buyer_id": str(buyer_id), "plan": "free"}
    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
    finally:
        conn.close()

# ---------------------------
# Buyer Request System (web + API)
# ---------------------------
@app.get("/buyers/request", response_class=HTMLResponse)
def buyer_request_form():
    return """
    <html><body style="font-family:Arial;max-width:800px;margin:25px auto">
    <h2>Buyer Request (Cars / Business / Real Estate)</h2>
    <form id="f">
      <label>Name</label><br/><input name="buyer_name" style="width:100%" required><br/><br/>
      <label>Email</label><br/><input name="buyer_email" type="email" style="width:100%" required><br/><br/>

      <label>Category</label><br/>
      <select name="category" style="width:100%">
        <option value="cars">cars</option>
        <option value="business">business</option>
        <option value="real_estate">real_estate</option>
      </select><br/><br/>

      <label>Location (optional)</label><br/><input name="location" style="width:100%"><br/><br/>

      <label>Min Budget</label><br/><input name="min_budget" type="number" style="width:100%" value="0"><br/><br/>
      <label>Max Budget</label><br/><input name="max_budget" type="number" style="width:100%" value="100000"><br/><br/>

      <label>Keywords (what you want)</label><br/>
      <input name="keywords" style="width:100%" placeholder="camry, laundromat, 3 bed, foreclosure"><br/><br/>

      <label>Notes</label><br/>
      <textarea name="notes" style="width:100%" rows="4"></textarea><br/><br/>

      <button type="submit">Create Request</button>
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
            insert into buyer_requests(
              buyer_email, buyer_name, category, location, min_budget, max_budget, keywords, notes, active
            )
            values (%s,%s,%s,%s,%s,%s,%s,%s,true)
            returning id
        """, (
            payload.get("buyer_email"),
            payload.get("buyer_name",""),
            (payload.get("category") or "cars").lower(),
            payload.get("location",""),
            float(payload.get("min_budget") or 0),
            float(payload.get("max_budget") or 10_000_000),
            payload.get("keywords",""),
            payload.get("notes",""),
        ))
        request_id = cur.fetchone()[0]
        conn.commit()
        cur.close()

        # confirmation email
        send_email(
            payload.get("buyer_email"),
            "VortexAI — Request Created",
            f"""
            <h3>Your request is live</h3>
            <p><b>Category:</b> {(payload.get("category") or "cars")}</p>
            <p><b>Location:</b> {payload.get("location","")}</p>
            <p><b>Budget:</b> ${int(payload.get("min_budget") or 0):,} - ${int(payload.get("max_budget") or 0):,}</p>
            <p><b>Keywords:</b> {payload.get("keywords","")}</p>
            <p>We will email you when deals match your request.</p>
            """
        )

        return {"status": "ok", "request_id": str(request_id)}
    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
    finally:
        conn.close()

# ---------------------------
# Deals JSON
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

# ---------------------------
# Request Matches (VIP/Elite only)
# ---------------------------
@app.get("/request-matches/{request_id}")
def list_request_matches(request_id: str, email: str):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # plan gate
        cur.execute("select plan from buyers where email=%s", (email,))
        buyer = cur.fetchone()
        if not buyer or buyer["plan"] not in ["vip", "elite"]:
            raise HTTPException(status_code=403, detail="Upgrade required (VIP/Elite)")

        cur.execute("""
            select rm.*, d.title, d.category, d.price, d.location, d.ai_score, d.estimated_fee
            from request_matches rm
            join deals d on d.id = rm.deal_id
            where rm.request_id = %s
            order by rm.match_score desc, rm.created_at desc
        """, (request_id,))

        rows = cur.fetchall()
        cur.close()
        return {"count": len(rows), "matches": rows}
    finally:
        conn.close()
