# worker/worker.py
import os
import time
import requests
from worker.sources_adapter import collect_deals

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")
RUN_EVERY_MINUTES = int(os.getenv("RUN_EVERY_MINUTES", "15"))

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
