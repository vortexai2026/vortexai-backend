import json
import requests
import uuid
from datetime import datetime

API_URL = "http://localhost:8080/deals/create"

with open("app/sources.json") as f:
    SOURCES = json.load(f)

def normalize_deal(raw, asset_type):
    return {
        "id": str(uuid.uuid4()),
        "title": raw.get("title", "Unknown"),
        "price": raw.get("price", 0),
        "location": raw.get("location", ""),
        "asset_type": asset_type,
        "source": raw.get("source", "unknown"),
        "status": "new",
        "created_at": datetime.utcnow().isoformat()
    }

def fake_scrape(source):
    # TEMP placeholder — later replaced with real scraping
    return [{
        "title": f"Sample deal from {source['name']}",
        "price": 50000,
        "location": "USA",
        "source": source["name"]
    }]

def run():
    for asset_type, sources in SOURCES.items():
        for source in sources:
            results = fake_scrape(source)

            for r in results:
                deal = normalize_deal(r, asset_type)
                requests.post(API_URL, json=deal)

if __name__ == "__main__":
    run()
