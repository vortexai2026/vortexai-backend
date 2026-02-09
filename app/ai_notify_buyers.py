from app.database import fetch_all, execute
from app.emailer import send_email

def notify_matching_buyers(deal_id: str):
    deal = fetch_all("SELECT * FROM deals WHERE id=%s", (deal_id,))
    if not deal:
        return

    deal = deal[0]

    buyers = fetch_all("""
        SELECT * FROM buyer_requests
        WHERE asset_type=%s
          AND min_price <= %s
          AND max_price >= %s
          AND status='active'
    """, (deal["asset_type"], deal["price"], deal["price"]))

    for b in buyers:
        if b.get("email"):
            body = f"""
New deal available:

{deal['title']}
Location: {deal['location']}
Price: {deal['price']}

Reply if interested.
"""
            send_email(b["email"], "New Deal Available", body)
