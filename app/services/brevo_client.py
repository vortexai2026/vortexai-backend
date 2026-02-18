import os
import httpx

BREVO_BASE = "https://api.brevo.com/v3"

def _headers():
    return {
        "api-key": os.environ["BREVO_API_KEY"],
        "accept": "application/json",
        "content-type": "application/json",
    }

async def brevo_post(path: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{BREVO_BASE}{path}", headers=_headers(), json=payload)
        r.raise_for_status()
        return r.json() if r.content else {"ok": True}
