# app/services/intent.py
def detect_intent(text):
    buyer_keywords = ["looking for", "need", "want to buy"]
    seller_keywords = ["for sale", "selling", "must sell"]

    text = text.lower()

    if any(k in text for k in buyer_keywords):
        return "buyer"
    if any(k in text for k in seller_keywords):
        return "seller"
    return "unknown"
