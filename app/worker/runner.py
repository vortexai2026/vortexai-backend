import time
from sources.craigslist import run_craigslist
from sources.bizbuysell import run_bizbuysell
from sources.cars_rss import run_cars

INTERVAL = 60 * 15  # every 15 minutes

while True:
    print("🚀 Automation cycle started")

    run_cars()
    run_craigslist()
    run_bizbuysell()

    print("⏳ Sleeping...")
    time.sleep(INTERVAL)
