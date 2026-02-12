from fastapi import APIRouter
from app.database import execute

router = APIRouter(prefix="/ingest", tags=["Ingest"])

@router.post("/deal")
def ingest_deal(payload: dict):
    """
    This endpoint receives deal data from bots / scrapers.
    """

    source = payload.get("source", "unknown")
    title = payload.get("title", "No Title")
    asset_type = payload.get("asset_type", "business")
    location = payload.get("location")
    url = payload.get("url")
    price = payload.get("price")
    currency = payload.get("currency", "USD")
    description = payload.get("description")

    execute("""
        INSERT INTO deals (source, title, asset_type, location, url, price, currency, description)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (source, title, asset_type, location, url, price, currency, description))

    return {"status": "success", "message": "Deal ingested"}

