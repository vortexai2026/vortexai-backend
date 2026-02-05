# app/services/match_engine.py
from app.db import db

def match_deal_to_buyers(deal):
    buyers = db.fetch_all("""
      SELECT * FROM buyers
      WHERE is_active = true
        AND :asset_type = ANY(asset_types)
        AND :location = ANY(cities)
        AND :price BETWEEN min_price AND max_price
      ORDER BY
        CASE tier
          WHEN 'vip' THEN 1
          WHEN 'pro' THEN 2
          ELSE 3
        END;
    """, {
        "asset_type": deal["asset_type"],
        "location": deal["location"],
        "price": deal["price"]
    })

    for buyer in buyers:
        db.execute("""
          INSERT INTO deal_matches (deal_id,buyer_id,score)
          VALUES (:deal_id,:buyer_id,90)
        """, {
            "deal_id": deal["id"],
            "buyer_id": buyer["id"]
        })
