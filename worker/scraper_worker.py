import json
import time
import uuid
import requests
from pathlib import Path

# ==============================
# PHASE 1 CONFIG (DO NOT RAISE YET)
# ==============================

API_URL = "http://localhost:8080/deals/create"  # Railway URL later
SOURCES_PATH = Path("data/sources_usa.json")

MAX_DEALS_PER_RUN = 20        # 🔒 PHASE 1 LIMIT
DELAY_BETWEEN_DEALS = 2       # seconds (safe throttle)

HEADERS = {
    "Content-Type": "application/json"
}

# ==============================
# HELPERS
# ==============================

def load_sources():
    if not SOURCES_PATH.exists():
        raise FileNotFoundError("sources_usa.json not found")
    with open(SOURCES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_deal(source_name, asset_type):
    return {
        "source": source_name,
        "external_id": str(uuid.uuid4()),
        "asset_type": asset_type,
        "title": f"{asset_type.title()} deal from {source_name}",
        "description": "Auto-ingested by VortexAI worker",
        "location": "USA",
        "url": "https://example.com",
        "price": 100000,
        "currency": "USD"
    }

def send_deal(deal):
    try:
        r = requests.post(API_URL, json=deal, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            print(f"✅ SENT | {deal['asset_type']} | {deal['source']}")
            return True
        else:
            print(f"❌ FAIL | {r.status_code} | {r.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR | {e}")
        return False

# ==============================
# MAIN RUNNER
# ==============================

def run():
    print("🚀 VortexAI Scraper Worker — PHASE 1")
    sources = load_sources()

    sent_count = 0

    for asset_type, items in sources.items():
        for src in items:

            if sent_count >= MAX_DEALS_PER_RUN:
                print("🛑 Phase-1 limit reached. Stopping.")
                return

            deal = build_deal(
                source_name=src["name"],
                asset_type=asset_type
            )

            if send_deal(deal):
                sent_count += 1

            time.sleep(DELAY_BETWEEN_DEALS)

    print(f"✅ DONE | Total deals sent: {sent_count}")

# ==============================
# ENTRY POINT
# ==============================

if __name__ == "__main__":
    run()
