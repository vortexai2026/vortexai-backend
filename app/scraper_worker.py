# worker/sources_adapter.py
from typing import List, Dict, Any
import requests

def collect_deals() -> List[Dict[str, Any]]:
    """
    SAFE MODE:
    - Use RSS feeds
    - Use partner APIs
    - Use your own listing feeds
    - Use manual uploads
    """
    deals: List[Dict[str, Any]] = []

    # Example: a "feed" that returns JSON (you can replace this)
    # resp = requests.get("https://your-safe-feed.com/deals.json", timeout=20)
    # for d in resp.json():
    #     deals.append(d)

    # For now: return empty list (won't crash)
    return deals
