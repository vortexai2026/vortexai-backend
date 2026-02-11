from typing import Dict, Any


def build_outreach_message(deal: Dict[str, Any], decision: str) -> Dict[str, str]:
    asset_type = (deal.get("asset_type") or "").lower()
    title = (deal.get("title") or "").strip()
    location = (deal.get("location") or "").strip()
    price = deal.get("price") or ""
    url = (deal.get("url") or "").strip()

    intro = "Hi! Is this still available?"
    if asset_type in ("real_estate", "house", "homes"):
        intro = "Hi! Is this property still available?"
    elif asset_type in ("car", "cars", "vehicle"):
        intro = "Hi! Is the vehicle still available?"
    elif asset_type in ("business", "businesses"):
        intro = "Hi! Is the business listing still available?"

    questions = ["What’s the reason for selling?", "Are you flexible on price if we move quickly?"]

    if asset_type in ("real_estate", "house", "homes"):
        questions = [
            "Are there any major repairs needed?",
            "Are you flexible on price if we can close quickly?",
            "What’s the reason for selling?"
        ]
    elif asset_type in ("car", "cars", "vehicle"):
        questions = [
            "Any issues with the engine or transmission?",
            "Do you have title/registration available?",
            "Are you flexible on price if we can pick up quickly?"
        ]
    elif asset_type in ("business", "businesses"):
        questions = [
            "What’s the reason for selling?",
            "Is seller financing available?",
            "What’s the approximate monthly profit?"
        ]

    lines = [
        intro,
        f"I’m interested in: {title}" if title else "I’m interested.",
        f"Location: {location}" if location else "",
        f"Price: {price}" if price != "" else "",
        "",
        "Quick questions:",
        *[f"- {q}" for q in questions],
        "",
        "Thanks!"
    ]

    body = "\n".join([l for l in lines if l]).strip()

    subject = "Quick question about your listing"
    if asset_type in ("real_estate", "house", "homes"):
        subject = "Quick question about your property"
    elif asset_type in ("car", "cars", "vehicle"):
        subject = "Quick question about your vehicle"

    if url:
        body += f"\n\nListing link: {url}"

    return {"subject": subject, "body": body}
