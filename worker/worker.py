import os
import time
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")
RUN_EVERY_MINUTES = int(os.getenv("RUN_EVERY_MINUTES", "15"))

def collect_deals():
    return [
        {
            "source": "facebook",
            "external_id": "demo123",
            "asset_type": "real_estate",
            "title": "Must sell house cash only",
            "location": "Winnipeg",
            "price": 120000,
            "url": "https://facebook.com/demo"
        }
    ]

def run():
    while True:
        for deal in collect_deals():
            requests.post(f"{BACKEND_URL}/deals/create", json=deal)
        time.sleep(RUN_EVERY_MINUTES * 60)

if __name__ == "__main__":
    run()
