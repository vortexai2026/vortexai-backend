import json
import uuid
import requests

API_URL = "http://localhost:8080/deals/create"

def load_sources():
    with open("app/data/sources.json", "r") as f:
        return json.load(f)

def post_deal(title, price, location, asset_type, source):
    deal = {
        "id": str(uuid.uuid4()),
        "title": title,
        "price": price,
        "location": location,
        "asset_type": asset_type,
        "source": source
    }
    r = requests.post(API_URL, json=deal, timeout=30)
    return r.status_code, r.text

def run_once():
    sources = load_sources()
    for asset_type, items in sources.items():
        for s in items:
            status, text = post_deal(
                title=f"Sample deal from {s['name']}",
                price=50000 if asset_type == "real_estate" else 7000,
                location="Winnipeg, MB" if s.get("country") == "Canada" else "Miami, FL",
                asset_type=asset_type,
                source=s["name"]
            )
            print("POST", s["name"], status)

if __name__ == "__main__":
    run_once()
