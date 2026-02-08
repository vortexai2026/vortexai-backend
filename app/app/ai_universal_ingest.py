from app.database import execute
from app.ai_text_classifier import classify_post
from app.ai_entity_parser import extract_price, extract_location

def ingest_post(source_name: str, category: str, raw_text: str):
    role = classify_post(raw_text)

    if role == "ignore":
        return {"status": "ignored"}

    price = extract_price(raw_text)
    location = extract_location(raw_text)

    if role == "seller":
        execute("""
            INSERT INTO deals (title, location, price, asset_type, source, decision)
            VALUES (%s, %s, %s, %s, %s, 'pending')
        """, (
            raw_text[:120],
            location,
            price,
            category,
            source_name
        ))
        return {"status": "seller_saved"}

    if role == "buyer":
        execute("""
            INSERT INTO buyer_requests (notes, location, asset_type, status)
            VALUES (%s, %s, %s, 'active')
        """, (
            raw_text,
            location,
            category
        ))
        return {"status": "buyer_saved"}
