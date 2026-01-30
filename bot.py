import os
import time
import random
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "").rstrip("/")
if not API_BASE_URL:
    raise RuntimeError("API_BASE_URL missing (example: https://vortexai-backend-production.up.railway.app)")

RUN_MODE = os.getenv("RUN_MODE", "loop")          # once | loop
SLEEP_SECONDS = int(os.getenv("SLEEP_SECONDS", "900"))  # 15 min

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

    return {
        "email": "auto@vortexai.com",
        "category": category,
        "location": random.choice(LOCATIONS),
        "price": random.randint(lo, hi),
        "description": f"[AUTO BOT] {category} deal - {random.choice(keywords[category])}"
    }

def run_once():
    # confirm server
    h = requests.get(f"{API_BASE_URL}/health", timeout=10)
    print("health:", h.status_code, h.text)

    for cat in CATEGORIES:
        deal = make_deal(cat)
        r = requests.post(f"{API_BASE_URL}/api/sell", json=deal, timeout=20)
        print("POST", r.status_code, deal["category"], deal["location"], deal["price"], r.text)
        time.sleep(1.0)

def main():
    if RUN_MODE == "once":
        run_once()
        return

    while True:
        run_once()
        print("sleep:", SLEEP_SECONDS)
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()
