def detect_intent(text: str) -> str:
    text = text.lower()

    buyer_keywords = [
        "looking for", "need", "want to buy",
        "searching for", "anyone have"
    ]

    seller_keywords = [
        "for sale", "selling", "must sell",
        "price drop", "urgent sale"
    ]

    if any(k in text for k in buyer_keywords):
        return "buyer"
    if any(k in text for k in seller_keywords):
        return "seller"
    return "unknown"
