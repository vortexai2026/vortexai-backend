from app.emailer import send_email

def take_action(deal: dict):
    subject = f"🔥 HOT DEAL: {deal['title']}"
    body = f"""
PRICE: {deal['price']}
TYPE: {deal['asset_type']}
LOCATION: {deal.get('location')}

AI SCORE: {deal['ai_score']}

CONTACT NOW.
"""

    send_email(subject, body)
