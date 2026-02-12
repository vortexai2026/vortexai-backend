# worker/match_buyers.py
from app.db import database as db

def match_buyers_for_deal(deal_id: int):
    # Fetch deal info
    deal = db.fetch_one("SELECT * FROM deals WHERE id = :id;", {"id": deal_id})
    if not deal:
        print(f"No deal found with id {deal_id}")
        return []

    # Match buyers by city, asset type, and price range
    matched_buyers = db.fetch_all(
        """
        SELECT * FROM buyers
        WHERE active = TRUE
        AND asset_type = :asset_type
        AND city = :city
        AND min_price <= :price
        AND max_price >= :price
        """,
        {"asset_type": deal["asset_type"], "city": deal["city"], "price": deal["price"]}
    )

    # Notify / log matched buyers
    for buyer in matched_buyers:
        print(f"Matched Buyer {buyer['name']} ({buyer['email']}) for Deal {deal_id}")
        # Optional: send email or push notification here

    return matched_buyers

# Standalone run for testing
if __name__ == "__main__":
    test_deal_id = 1  # replace with a real deal id
    matches = match_buyers_for_deal(test_deal_id)
    print(f"Total matches found: {len(matches)}")
