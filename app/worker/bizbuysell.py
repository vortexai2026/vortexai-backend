import requests

API = "https://vortexai-backend-production.up.railway.app/api/sell"

def run_bizbuysell():
    # Placeholder for RSS / newsletter parsing
    deal = {
        "email": "auto@vortexai.com",
        "category": "business",
        "location": "USA",
        "price": 150000,
        "description": "Auto business lead"
    }

    requests.post(API, json=deal, timeout=10)
