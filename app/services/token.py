import secrets
from datetime import datetime, timedelta, timezone

def new_token() -> str:
    return secrets.token_urlsafe(24)

def expires_in(hours: int = 48):
    return datetime.now(timezone.utc) + timedelta(hours=hours)
