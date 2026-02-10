from typing import Dict, Any

def build_outreach_message(deal: Dict[str, Any], decision: str) -> Dict[str, str]:
    asset_type = (deal.get("asset_type") or "").lower()
    title = (deal.get("title") or "").strip()
    location = (deal.get("location") or "").strip()
    price = deal.get("price")
    url = (deal.get("url") or "").strip()

    intro = "Hi! Is this still available?"
    if asset_type in ("real_estate", "house", "homes"):
        intro = "Hi! Is this property still available?"
    elif asset_type in ("cars", "car", "vehicle"):
        intro = "Hi! Is the vehicle still available?"
    elif asset_type in ("businesses", "business"):
        intro = "Hi! Is the business listing still available?"

    if asset_type in ("real_estate", "house", "homes"):
        questions = [
            "Are there any major repairs needed?",
            "Are you flexible on price if we can close quickly?",
            "What’s the reason for selling?",
        ]
        subject = "Quick question about your property"
    elif asset_type in ("cars", "car", "vehicle"):
        questions = [
            "Any issues with the engine or transmission?",
            "Do you have the title/registration available?",
            "Are you flexible on price if we can pick up quickly?",
        ]
        subject = "Quick question about your vehicle"
    elif asset_type in ("businesses", "business"):
        questions = [
            "What’s the reason for selling?",
            "Is there seller financing available?",
            "What’s the approximate monthly profit?",
        ]
        subject = "Quick question about your business listing"
    else:
        questions = [
            "What’s the reason for selling?",
            "Are you flexible on price if we move quickly?",
        ]
        subject = "Quick question about your listing"

    lines = [
        intro,
        f"I’m interested in: {title}" if title else "I’m interested.",
        f"Location: {location}" if location else "",
        f"Price: {price}" if price is not None else "",
        "",
        "Quick questions:",
        *[f"- {q}" for q in questions],
        "",
        "Thanks! Quick replies are perfect.",
    ]
    body = "\n".join([l for l in lines if l]).strip()
    if url:
        body += f"\n\nListing link: {url}"

    return {"subject": subject, "body": body}
