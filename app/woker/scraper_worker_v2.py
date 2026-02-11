import time
import uuid
import requests
import random

API_URL = "https://vortexai-backend-production.up.railway.app/deals/create"

SOURCES = [
    {"name": "Craigslist Canada", "country": "CA"},
    {"name": "Facebook Marketplace CA", "country": "CA"},
    {"name": "Craigslist USA", "country": "US"},
    {"name": "Facebook Marketplace US", "country": "US"},
]

ASSET_TYPES = ["real_estate", "cars", "business"]

CITIES = {
    "CA": ["Winnipeg, MB", "Toronto, ON", "Calgary, AB"],
    "US": ["Phoenix, AZ", "Dallas, TX", "Tampa, FL"],
}

def generate_deal():
    source = random.choice(SOURCES)
    asset_type = random.choice(ASSET_TYPES)
    city = random.choice(CITIES[source["country"]])

    price = random.randint(50000, 400000)

    return {
        "source": source["name"],
        "external_id": str(uuid.uuid4()),
        "asset_type": asset_type,
        "title": f"{city} {asset_type.replace('_', ' ').title()} – Motivated Seller",
        "description": "Urgent sale. Seller needs fast close.",
        "location": city,
        "url": "https://example.com",
        "price": price,
        "currency": "CAD" if source["country"] == "CA" else "USD",
    }

def run(batch_size=10, delay=5):
    print("🚀 Scraper Worker v2 started")

    for i in range(batch_size):
        deal = generate_deal()
        try:
            r = requests.post(API_URL, json=deal, timeout=10)
            if r.status_code == 200:
                print(f"✅ {i+1}/{batch_size} {deal['title']}")
            else:
                print(f"❌ {r.status_code} {r.text}")
        except Exception as e:
            print("⚠️ Error:", e)

        time.sleep(delay)

if __name__ == "__main__":
    run(batch_size=10, delay=4)
