import json
import time
import requests
import uuid
from pathlib import Path

# =========================
# CONFIG
# =========================

API_URL = "https://vortexai-backend-production.up.railway.app/deals/create"
SOURCES_PATH = Path("data/sources_usa.json")

HEADERS = {
    "Content-Type": "application/json"
}

DELAY_SECONDS = 2  # throttle (safe)

# =========================
# LOAD SOURCES
# =========================

def load_sources():
    with open(SOURCES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# =========================
# BUILD DEAL (THIS WAS MISSING)
# =========================

def build_deal(source_name, asset_type, country):
    return {
        "source": source_name,
        "external_id": str(uuid.uuid4()),
        "asset_type": asset_type,
        "title": f"{asset_type.replace('_', ' ').title()} deal from {source_name}",
        "description": "Auto-ingested by VortexAI worker",
        "location": "Winnipeg" if country == "CANADA" else "Texas",
        "country": country,                     # ✅ REQUIRED
        "url": "https://example.com",
        "price": 320000,                        # ✅ INTEGER ONLY
        "currency": "CAD" if country == "CANADA" else "USD"
    }

# =========================
# SEND DEAL
# =========================

def send_deal(deal):
    try:
        r = requests.post(API_URL, json=deal, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            print("❌ Failed:", r.text)
        else:
            print("✅ Sent:", deal["title"], "|", deal["country"])
    except Exception as e:
        print("❌ Error sending deal:", e)

# =========================
# MAIN WORKER LOOP
# =========================

def run():
    sources = load_sources()

    for asset_type, source_list in sources.items():
        for src in source_list:
            country = src.get("country", "USA")  # default safe

            deal = build_deal(
                source_name=src["name"],
                asset_type=asset_type,
                country=country
            )

            send_deal(deal)
            time.sleep(DELAY_SECONDS)

# =========================
# ENTRY
# =========================

if __name__ == "__main__":
    print("🚀 VortexAI Scraper Worker v1 started")
    run()

