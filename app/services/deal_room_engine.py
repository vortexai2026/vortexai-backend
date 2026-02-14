import secrets

def generate_deal_room_token():
    return secrets.token_urlsafe(32)
