import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.deal import Deal
from app.models.buyer import Buyer


FREE_DELAY_SECONDS = 900  # 15 minutes


async def notify_buyer_of_match(
    db: AsyncSession,
    deal: Deal,
    buyer: Buyer,
) -> None:

    if buyer.tier == "free":
        print(f"[DELAYED ALERT] {buyer.email} will receive deal in 15 minutes")
        asyncio.create_task(delayed_notification(deal, buyer))
        return

    # Pro / Elite → instant
    print(f"[INSTANT ALERT] {buyer.email} matched to {deal.title} (${deal.price})")


async def delayed_notification(deal: Deal, buyer: Buyer):
    await asyncio.sleep(FREE_DELAY_SECONDS)

    print(f"[FREE ALERT SENT] {buyer.email} received delayed deal {deal.title}")
