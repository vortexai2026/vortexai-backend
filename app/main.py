import stripe
from fastapi import HTTPException
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

app = FastAPI(title="VortexAI", version="7.0")

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

# ---------------------------
# AI scoring (works now)
# ---------------------------

def clamp(n, lo=0, hi=100):
    return max(lo, min(hi, int(n)))

def score_deal(deal: dict) -> dict:
    asset = (deal.get("asset_type") or "").lower()
    price = float(deal.get("price") or 0)
    desc = (deal.get("description") or "").lower()

    profit = 50
    urgency = 50
    risk = 50

    # Price heuristics
    if price <= 5000:
        profit += 25
    elif price <= 20000:
        profit += 15
    elif price >= 200000:
        profit -= 10

    hot_words = ["must sell", "urgent", "today", "moving", "foreclosure", "repo", "auction", "liquidation", "clearance"]
    bad_words = ["salvage", "engine knock", "no title", "scam", "broken", "parts only"]

    if any(w in desc for w in hot_words):
        urgency += 25
        profit += 10

    if any(w in desc for w in bad_words):
        risk += 30
        profit -= 15

    if asset in ["wholesale", "collectibles"]:
        profit += 10
    if asset in ["cars", "equipment"]:
        risk += 5

    ai_score = clamp((profit * 0.45) + (urgency * 0.30) + ((100 - risk) * 0.25))

    return {
        "profit_estimate": max(0, int(price * (ai_score / 200))),  # simple estimate
        "ai_score": ai_score
    }

# ---------------------------
# Buyer matching
# ---------------------------

def match_buyers_for_deal(conn, deal: dict):
    """
    Matches buyers by:
    - asset_type included in asset_types (comma separated string)
    - budget range
    - optional location contains buyer location (if buyer set one)
    Returns list of (buyer_id, match_score)
    """
    asset = (deal.get("asset_type") or "").lower()
    price = float(deal.get("price") or 0)
    location = (deal.get("location") or "").lower()
    ai_score = int(deal.get("ai_score") or 50)

    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from buyers order by created_at desc")
    buyers = cur.fetchall()
    cur.close()

    matches = []
    for b in buyers:
        types = (b.get("asset_types") or "").lower()
        if asset not in types:
            continue

        min_b = float(b.get("min_budget") or 0)
        max_b = float(b.get("max_budget") or 10_000_000)
        if not (min_b <= price <= max_b):
            continue

        buyer_loc = (b.get("location") or "").lower().strip()
        if buyer_loc and buyer_loc not in location:
            continue

        # match_score: weight deal ai_score + closeness to budget
        budget_mid = (min_b + max_b) / 2 if (min_b + max_b) > 0 else price
        budget_score = 100 - min(100, int(abs(price - budget_mid) / max(1, budget_mid) * 100))
        match_score = clamp(int(ai_score * 0.7 + budget_score * 0.3))

        matches.append((str(b["id"]), match_score))

    return matches

def save_matches(conn, deal_id: str, matches: list):
    cur = conn.cursor()
    for buyer_id, match_score in matches:
        cur.execute(
            """
            insert into deal_matches(deal_id, buyer_id, match_score, status)
            values (%s, %s, %s, 'matched')
            """,
            (deal_id, buyer_id, int(match_score))
        )
    cur.close()

# ---------------------------
# Health
# ---------------------------

@app.get("/health")
def health():
    return {"status": "ok", "service": "VortexAI", "version": "7.0"}

# ---------------------------
# Simple Web Home
# ---------------------------

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html><body style="font-family:Arial;padding:25px;max-width:900px;margin:auto">
      <h1>VortexAI ✅ Running</h1>
      <ul>
        <li><a href="/sell">Seller: Submit Deal</a></li>
        <li><a href="/buyers/apply">Buyer: Register</a></li>
        <li><a href="/dealers/apply">Dealer: Register</a></li>
        <li><a href="/deals">View Deals (JSON)</a></li>
      </ul>
      <p style="color:#666">Tip: After a seller submits a deal, the system auto-scores it and auto-matches buyers.</p>
    </body></html>
    """

# ---------------------------
# Sellers (web form + API)
# ---------------------------

@app.get("/sell", response_class=HTMLResponse)
def seller_form():
    return """
    <html><body style="font-family:Arial;max-width:700px;margin:25px auto">
    <h2>Seller Portal — Submit a Deal</h2>
    <form id="f">
      <label>Name</label><br/><input name="name" style="width:100%" required><br/><br/>
      <label>Phone</label><br/><input name="phone" style="width:100%"><br/><br/>
      <label>Asset Type</label><br/>
      <select name="asset_type" style="width:100%">
        <option value="cars">cars</option>
        <option value="wholesale">wholesale</option>
        <option value="collectibles">collectibles</option>
        <option value="equipment">equipment</option>
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
def seller_submit(payload: dict):
    """
    1) Insert seller
    2) Insert deal
    3) AI score
    4) Auto-match buyers
    5) Save matches
    """
    conn = get_conn()
    try:
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

        # score deal
        deal = {
            "title": f"{payload.get('asset_type','deal')} in {payload.get('location','')}",
            "asset_type": payload.get("asset_type"),
            "price": payload.get("price"),
            "location": payload.get("location"),
            "description": payload.get("description",""),
        }
        scores = score_deal(deal)
        deal.update(scores)

        cur.execute("""
            insert into deals(title, asset_type, price, location, seller_id, ai_score)
            values (%s,%s,%s,%s,%s,%s)
            returning id
        """, (
            deal["title"],
            deal["asset_type"],
            deal["price"],
            deal["location"],
            str(seller_id),
            int(deal["ai_score"]),
        ))
        deal_id = cur.fetchone()[0]
        cur.close()

        # match buyers + store matches
        matches = match_buyers_for_deal(conn, {"id": str(deal_id), **deal})
        save_matches(conn, str(deal_id), matches)

        conn.commit()

        return {
            "status": "ok",
            "seller_id": str(seller_id),
            "deal_id": str(deal_id),
            "ai_score": int(deal["ai_score"]),
            "profit_estimate": int(deal["profit_estimate"]),
            "matches": len(matches),
        }
    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
    finally:
        conn.close()

# ---------------------------
# Buyers (web form + API)
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
      <label>Asset Types (comma separated)</label><br/>
      <input name="asset_types" style="width:100%" value="cars,wholesale,collectibles,equipment"><br/><br/>
      <label>Min Budget</label><br/><input name="min_budget" type="number" style="width:100%" value="0"><br/><br/>
      <label>Max Budget</label><br/><input name="max_budget" type="number" style="width:100%" value="100000"><br/><br/>
      <label>Location (optional)</label><br/><input name="location" style="width:100%"><br/><br/>
      <button type="submit">Register</button>
    </form>
    <pre id="out" style="background:#f6f6f6;padding:12px;margin-top:15px;border-radius:8px"></pre>
    <script>
      document.getElementById("f").addEventListener("submit", async (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        const obj = Object.fromEntries(fd.entries());
        obj.min_budget = Number(obj.min_budget);
        obj.max_budget = Number(obj.max_budget);
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
            insert into buyers(name, email, phone, asset_types, min_budget, max_budget, location)
            values (%s,%s,%s,%s,%s,%s,%s)
            returning id
        """, (
            payload.get("name"),
            payload.get("email"),
            payload.get("phone"),
            payload.get("asset_types") or "cars,wholesale,collectibles,equipment",
            payload.get("min_budget") or 0,
            payload.get("max_budget") or 10000000,
            payload.get("location") or "",
        ))
        buyer_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return {"status": "ok", "buyer_id": str(buyer_id)}
    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
    finally:
        conn.close()

# ---------------------------
# Dealers (web form + API)
# ---------------------------

@app.get("/dealers/apply", response_class=HTMLResponse)
def dealer_form():
    return """
    <html><body style="font-family:Arial;max-width:700px;margin:25px auto">
    <h2>Dealer Registration</h2>
    <form id="f">
      <label>Company</label><br/><input name="company" style="width:100%" required><br/><br/>
      <label>Contact Name</label><br/><input name="contact_name" style="width:100%" required><br/><br/>
      <label>Email</label><br/><input name="email" type="email" style="width:100%" required><br/><br/>
      <label>Phone</label><br/><input name="phone" style="width:100%"><br/><br/>
      <label>Deal Types (comma separated)</label><br/>
      <input name="deal_types" style="width:100%" value="cars,wholesale,collectibles,equipment"><br/><br/>
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
            insert into dealers(company, contact_name, phone, email, deal_types)
            values (%s,%s,%s,%s,%s)
            returning id
        """, (
            payload.get("company"),
            payload.get("contact_name"),
            payload.get("phone"),
            payload.get("email"),
            payload.get("deal_types") or "cars,wholesale,collectibles,equipment",
        ))
        dealer_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return {"status": "ok", "dealer_id": str(dealer_id)}
    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
    finally:
        conn.close()

# ---------------------------
# Deals + Matches (JSON endpoints)
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

@app.get("/matches/{deal_id}")
def list_matches_for_deal(deal_id: str):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            select dm.*, b.name as buyer_name, b.email as buyer_email
            from deal_matches dm
            join buyers b on b.id = dm.buyer_id
            where dm.deal_id = %s
            order by dm.match_score desc
        """, (deal_id,))
        rows = cur.fetchall()
        cur.close()
        return {"count": len(rows), "matches": rows}
    finally:
        conn.close()

