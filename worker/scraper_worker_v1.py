import json
import time
import uuid
import requests
from pathlib import Path
from datetime import datetime

# =========================
# CONFIG
# =========================

API_URL = "https://vortexai-backend-production.up.railway.app/deals/create"
SOURCES_PATH = Path("data/sources_usa.json")  # you can add sources_canada.json later

HEADERS = {
    "Content-Type": "application/json"
}

DELAY_SECONDS = 3  # throttle (safe start)

# =========================
# LOAD SOURCES
# =========================

def load_sources():
    with open(SOURCES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# =========================
# BUILD CLEAN DEAL
# =========================

def build_deal(source, category):
    return {
        "source": source["name"],
        "external_id": str(uuid.uuid4()),
        "asset_type": category,                # REQUIRED
        "title": f"{category.title()} deal from {source['name']}",
        "description": source.get("description", "Auto-ingested deal"),
        "location": source.get("location", "USA"),
        "country": source.get("country", "USA"),
        "url": source.get("url", "https://example.com"),
        "price": int(source.get("example_price", 100000)),  # INTEGER ONLY
        "currency": source.get("currency", "USD"),
        "created_at": datetime.utcnow().isoformat()
    }

# =========================
# SEND DEAL
# =========================

def send_deal(deal):
    try:
        r = requests.post(API_URL, json=deal, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            print(f"✅ Sent: {deal['title']} | {deal['price']} {deal['currency']}")
        else:
            print(f"❌ Failed ({r.status_code}): {r.text}")
    except Exception as e:
        print("❌ Error:", e)

# =========================
# RUN WORKER
# =========================

def run():
    sources = load_sources()

    for category, source_list in sources.items():
        for source in source_list:
            deal = build_deal(source, category)
            send_deal(deal)
            time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    print("🚀 scraper_worker_v1 started")
    run()
