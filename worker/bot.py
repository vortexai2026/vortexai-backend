import os
import time
import random
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "").rstrip("/")
if not API_BASE_URL:
    raise RuntimeError("API_BASE_URL missing. Example: https://vortexai-backend-production.up.railway.app")

RUN_MODE = os.getenv("RUN_MODE", "loop")  # once | loop
SLEEP_SECONDS = int(os.getenv("SLEEP_SECONDS", "900"))  # 15 minutes default

# Start with 3 categories (what you said):
CATEGORIES = ["business", "real_estate", "cars"]

LOCATIONS = [
    "Winnipeg, MB", "Toronto, ON", "Calgary, AB", "Vancouver, BC",
    "Miami, FL", "Dallas, TX", "Phoenix, AZ", "New York, NY"
]

def make_deal(category: str) -> dict:
    price_ranges = {
        "cars": (1500, 25000),
        "business": (30000, 250000),
        "real_estate": (50000, 350000),
    }
    lo, hi = price_ranges.get(category, (1000, 100000))

    keywords = {
        "cars": ["urgent", "must sell", "clean title", "price reduced"],
        "business": ["owner retiring", "cashflow", "urgent sale", "turnkey"],
        "real_estate": ["motivated seller", "foreclosure", "auction", "must sell"],
    }

    loc = random.choice(LOCATIONS)
    price = random.randint(lo, hi)
    hint = random.choice(keywords.get(category, ["deal"]))

    return {
        "email": "auto@vortexai.com",
        "category": category,
        "location": loc,
        "price": price,
        "description": f"[AUTO] {category} lead - {hint} - posted by bot"
    }

def post_deal(deal: dict):
    url = f"{API_BASE_URL}/api/sell"
    r = requests.post(url, json=deal, timeout=20)
    try:
        j = r.json()
    except:
        j = {"raw": r.text}

    print("POST", r.status_code, deal["category"], deal["location"], deal["price"], j)
    return r.status_code

def run_once():
    # Confirm backend is live
    h = requests.get(f"{API_BASE_URL}/health", timeout=10)
    print("health:", h.status_code, h.text)

    sent = 0
    for cat in CATEGORIES:
        deal = make_deal(cat)
        post_deal(deal)
        sent += 1
        time.sleep(1.0)  # be polite
    print("✅ sent:", sent)

def main():
    if RUN_MODE == "once":
        run_once()
        return

    while True:
        run_once()
        print(f"⏳ sleep {SLEEP_SECONDS}s")
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()
