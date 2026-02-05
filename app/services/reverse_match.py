from app.services.intent import detect_intent
from app.db import db
from app.ai import ask_ai


def reverse_match(post: dict):
    """
    post example:
    {
      "text": "Looking for a house in Winnipeg under 300k",
      "author": "John D",
      "source": "facebook"
    }
    """

    intent = detect_intent(post["text"])

    if intent != "buyer":
        return None

    # 🔹 AI extracts buyer preferences
    ai = ask_ai(f"""
    Extract buyer preferences from the message.
    Return JSON ONLY.

    Message:
    "{post['text']}"

    JSON format:
    {{
      "asset_type": "real_estate | car | truck | business | other",
      "city": "city name",
      "min_price": number,
      "max_price": number
    }}
    """)

    buyer = {
        "name": post.get("author", "Unknown Buyer"),
        "email": None,
        "phone": None,
        "asset_types": [ai["asset_type"]],
        "cities": [ai["city"]],
        "min_price": ai["min_price"],
        "max_price": ai["max_price"],
        "tier": "free"
    }

    buyer_id = db.fetch_one("""
        INSERT INTO buyers
        (name,email,phone,asset_types,cities,min_price,max_price,tier)
        VALUES
        (:name,:email,:phone,:asset_types,:cities,:min_price,:max_price,:tier)
        RETURNING id;
    """, buyer)["id"]

    match_existing_deals_to_buyer(buyer_id)

    return {"buyer_id": buyer_id}
