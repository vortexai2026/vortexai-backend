from app.db import db


def match_existing_deals_to_buyer(buyer_id):
    buyer = db.fetch_one(
        "SELECT * FROM buyers WHERE id = :id",
        {"id": buyer_id}
    )

    deals = db.fetch_all("""
      SELECT * FROM deals
      WHERE asset_type = ANY(:asset_types)
        AND location = ANY(:cities)
        AND price BETWEEN :min_price AND :max_price
    """, {
        "asset_types": buyer["asset_types"],
        "cities": buyer["cities"],
        "min_price": buyer["min_price"],
        "max_price": buyer["max_price"]
    })

    for deal in deals:
        db.execute("""
          INSERT INTO deal_matches (deal_id,buyer_id,score)
          VALUES (:deal_id,:buyer_id,85)
        """, {
            "deal_id": deal["id"],
            "buyer_id": buyer_id
        })
