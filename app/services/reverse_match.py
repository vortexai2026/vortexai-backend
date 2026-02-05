# app/services/reverse_match.py
from app.ai import ask_ai
from app.db import db
from app.services.match_engine import match_existing_deals_to_buyer
from app.services.intent import detect_intent

def reverse_match(post: dict):
    """
    post example:
    {
      "text": "Looking for a house in Winnipeg under 300k",
      "source": "facebook",
      "author": "John D"
    }
    """

    intent = detect_intent(post["text"])

    if intent != "buyer":
        return None
