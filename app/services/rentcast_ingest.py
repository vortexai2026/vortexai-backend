import os
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.deal import Deal
from app.services.scoring import score_deal

RENTCAST_API_KEY = os.getenv("RENTCAST_API_KEY")


async def pull_deals(db: AsyncSession, limit: int = 20):
    """
    Pull distressed properties from RentCast
    Create Deal objects
    Score them
    Save to DB
    """

    if not RENTCAST_API_KEY:
        return {"error": "RENTCAST_API_KEY not set"}

    url = "https://api.rentcast.io/v1/listings/sale"

    headers = {
        "X-Api-Key": RENTCAST_API_KEY
    }

    params = {
        "status": "active",
        "limit": limit
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return {"error": "RentCast request failed"}

    data = response.json()

    created = 0

    for item in data:

        deal = Deal(
            address=item.get("formattedAddress"),
            city=item.get("city"),
            state=item.get("state"),
            zip_code=item.get("zipCode"),
            seller_price=item.get("price"),
            arv_estimated=item.get("price"),  # temporary
            square_feet=item.get("squareFootage"),
            year_built=item.get("yearBuilt"),
            beds=item.get("bedrooms"),
            baths=item.get("bathrooms"),
        )

        score_deal(deal)

        db.add(deal)
        created += 1

    await db.commit()

    return {"created": created}
