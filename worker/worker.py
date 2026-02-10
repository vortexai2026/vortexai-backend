# worker/worker.py
import os
import time
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")
RUN_EVERY_MINUTES = int(os.getenv("RUN_EVERY_MINUTES", "15"))


def collect_deals():
    """
    Replace this with real scrapers.
    For now this returns demo deals so your pipeline proves working.
    """
    return [
        {
            "source": "demo",
            "external_id": "demo-001",
            "asset_type": "cars",
            "title": "Moving sale - 2012 Honda Civic need gone today",
            "description": "Runs good, must sell ASAP",
            "location": "Winnipeg, MB",
            "url": "https://example.com/car1",
            "price": 3500,
            "currency": "CAD",
        },
        {
            "source": "demo",
            "external_id": "demo-002",
            "asset_type": "real_estate",
            "title": "Motivated seller - house needs work - price reduced",
            "description": "Quick sale, cash preferred",
            "location": "Winnipeg, MB",
            "url": "https://example.com/house1",
            "price": 120000,
            "currency": "CAD",
        },
    ]


def push_deal(deal):
    r = requests.post(f"{BACKEND_URL}/deals/create", json=deal, timeout=30)
    r.raise_for_status()
    return r.json()


def run_once():
    deals = collect_deals()
    print(f"[worker] collected {len(deals)} deals")

    for d in deals:
        try:
            res = push_deal(d)
            print("[worker] pushed:", res.get("id"), res.get("decision"), res.get("scores"))
        except Exception as e:
            print("[worker] error pushing deal:", str(e))


def main():
    while True:
        run_once()
        sleep_seconds = RUN_EVERY_MINUTES * 60
        print(f"[worker] sleeping {RUN_EVERY_MINUTES} minutes...")
        time.sleep(sleep_seconds)


if __name__ == "__main__":
    main()
