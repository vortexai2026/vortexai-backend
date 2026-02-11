import uuid
from app.database import fetch_all, execute

def match_buyers_for_deal(deal: dict):
    """
    Rule-based matching:
    - same asset_type
    - active buyers
    - deal price within buyer min/max
    """

    price = deal.get("price") or 0
    asset_type = deal.get("asset_type")
    location = (deal.get("location") or "").lower()

    buyers = fetch_all("""
        SELECT *
        FROM buyers
        WHERE active = TRUE
          AND asset_type = %s
          AND %s BETWEEN min_price AND max_price
    """, (asset_type, price))

    matches = []

    for buyer in buyers:
        # Optional city filter (soft match)
        buyer_city = (buyer.get("city") or "").lower()
        if buyer_city and buyer_city not in location:
            continue

        match_id = str(uuid.uuid4())
        execute("""
            INSERT INTO deal_matches (id, deal_id, buyer_id)
            VALUES (%s, %s, %s)
        """, (
            match_id,
            deal["id"],
            buyer["id"]
        ))

        matches.append({
            "buyer_id": buyer["id"],
            "email": buyer["email"]
        })

    return matches
