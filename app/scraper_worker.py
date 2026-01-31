import os
import json
import time
import uuid
from app.database import execute

BASE_DIR = os.path.dirname(__file__)
CONFIG_DIR = os.path.join(BASE_DIR, "config")

SCRAPE_EVERY_SECONDS = int(os.getenv("SCRAPE_EVERY_SECONDS", "900"))

def load_json(name):
    with open(os.path.join(CONFIG_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)

def fake_scrape_one(asset_type: str, country: str, source: str, city: str) -> dict:
    # placeholder: replace later with real scrapers
    return {
        "id": str(uuid.uuid4()),
        "title": f"{asset_type.upper()} deal from {source} in {city}",
        "location": city,
        "price": 10000,
        "asset_type": asset_type,
        "source": source,
        "url": f"https://example.com/{source}/{uuid.uuid4()}",
        "market_value": 14000,
        "motivation": "high",
        "days_on_market": 7
    }

def insert_deal(d: dict):
    execute("""
        INSERT INTO deals (id, title, location, price, asset_type, source, url, market_value, motivation, days_on_market)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO NOTHING
    """, (
        d["id"], d["title"], d["location"], d["price"], d["asset_type"], d["source"],
        d["url"], d["market_value"], d["motivation"], d["days_on_market"]
    ))

def run_once():
    cities = load_json("cities_us_ca.json")
    sources = load_json("sources_master.json")

    for asset_type, by_country in sources.items():
        for country, source_list in by_country.items():
            for city in cities.get(country, []):
                for source in source_list:
                    d = fake_scrape_one(asset_type, country, source, city)
                    insert_deal(d)
                    print("Inserted", d["title"])

def loop():
    while True:
        run_once()
        time.sleep(SCRAPE_EVERY_SECONDS)

if __name__ == "__main__":
    loop()
