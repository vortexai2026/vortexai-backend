# app/services/offer_letter_engine.py

from datetime import datetime

def build_offer_email(deal, offer_price: float):
    """
    Simple, seller-friendly email.
    """
    title = deal.title or "your property"
    city = deal.city or ""
    subject = f"Cash Offer for {title} ({city})"

    body = f"""Hi,

I’m reaching out about {title}.

I can offer ${int(offer_price):,} cash, purchase AS-IS, and close quickly if the title is clear.

If that works, reply “YES” and I’ll send a simple purchase agreement for review.

Thanks,
Vortex AI Deals
"""
    return subject, body


def build_offer_letter_text(deal, offer_price: float):
    """
    A simple offer letter that can be used for PDF generation.
    """
    title = deal.title or "Property"
    city = deal.city or ""
    today = datetime.utcnow().strftime("%Y-%m-%d")

    letter = f"""OFFER TO PURCHASE (AS-IS)

Date: {today}

Property: {title}
Market: {city}

Offer Price: ${int(offer_price):,} (cash)

Terms:
- Purchase AS-IS
- Buyer pays with cash or private funds
- Closing timeline: 7–21 days (or faster if needed)
- Subject to clear title and standard closing process

If accepted, reply “YES” and we will send the purchase agreement immediately.

Signed,
Vortex AI Deals
"""
    return letter
