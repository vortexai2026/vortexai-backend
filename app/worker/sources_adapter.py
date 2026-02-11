from typing import List, Dict, Any
import os

def collect_deals() -> List[Dict[str, Any]]:
    """
    SAFE VERSION:
    - This is a placeholder collector.
    - For Facebook Marketplace: do NOT auto-DM bots. Use manual approval.
    - Ingestion can be:
        1) Manual CSV upload
        2) Email leads forwarded to webhook
        3) Partner feeds / official APIs
        4) Scrape sources that allow it
    """
    # Example deals (replace with real collectors)
    return [
        {
            "source": "Manual Upload",
            "external_id": "test-1",
            "asset_type": "cars",
            "title": "2012 Honda Civic - must sell today",
            "description": "Runs good, moving ASAP",
            "location": "Winnipeg, MB",
            "url": "https://example.com",
            "price": 2800,
            "currency": "CAD"
        }
    ]
