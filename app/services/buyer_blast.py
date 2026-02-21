from sqlalchemy import select
from app.models.buyer import Buyer


async def blast_green_deals(db, deal):
    """
    Finds matching buyers for a green deal
    and returns how many matches were found.
    (No email sending yet — just matching logic)
    """

    # Match by city (simple version)
    result = await db.execute(
        select(Buyer).where(Buyer.city == deal.city)
    )
    buyers = result.scalars().all()

    count = 0

    for buyer in buyers:
        # You can later add email/sms logic here
        count += 1

    return count
