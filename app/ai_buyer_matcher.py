import uuid
from app.database import fetch_all, execute


def match_buyers_to_deal(deal: dict):
    """
    Match buyers based on:
      - asset_type
      - city (optional)
      - min_price/max_price
    Creates rows in buyer_matches
    Returns list of matched buyers
    """
    price = float(deal.get("price") or 0)
    asset_type = (deal.get("asset_type") or "").lower().strip()
    location = (deal.get("location") or "")

    buyers = fetch_all("""
        SELECT *
        FROM buyers
        WHERE active = TRUE
          AND asset_type = %s
          AND min_price <= %s
          AND max_price >= %s
    """, (asset_type, price, price))

    matched = []

    for b in buyers:
        # city filter if buyer set city
        buyer_city = (b.get("city") or "").strip().lower()
        if buyer_city and location:
            if buyer_city not in location.lower():
                continue

        match_id = str(uuid.uuid4())
        # prevent duplicates: same buyer+deal
        execute("""
            INSERT INTO buyer_matches (id, buyer_id, deal_id, notified)
            VALUES (%s,%s,%s,FALSE)
            ON CONFLICT DO NOTHING
        """, (match_id, str(b["id"]), str(deal["id"])))

        matched.append(b)

    return matched
