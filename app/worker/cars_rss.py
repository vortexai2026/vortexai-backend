import requests

API = "https://vortexai-backend-production.up.railway.app/api/sell"

RSS_FEEDS = [
    "https://craigslist.org/search/cta?format=rss"
]

def run_cars():
    for feed in RSS_FEEDS:
        r = requests.get(feed, timeout=10)
        if r.status_code != 200:
            continue

        # VERY SIMPLE PARSE (upgrade later)
        items = r.text.split("<item>")[1:6]

        for item in items:
            deal = {
                "email": "auto@vortexai.com",
                "category": "cars",
                "location": "Unknown",
                "price": 5000,
                "description": "Auto car lead from RSS"
            }

            requests.post(API, json=deal, timeout=10)
