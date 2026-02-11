# app/notify_buyers.py
from app.emailer import send_email

def notify_buyers(deal, buyers):
    for buyer in buyers:
        subject = "🔥 New Deal Matches Your Criteria"
        body = f"""
Deal Found:

Title: {deal['title']}
Price: {deal['price']}
Location: {deal['location']}
Link: {deal['url']}

Reply YES if interested.
"""
        send_email(subject, body, buyer["email"])
