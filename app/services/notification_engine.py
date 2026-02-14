# app/services/notification_engine.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.deal import Deal
from app.models.buyer import Buyer


async def notify_buyer_of_match(
    db: AsyncSession,
    deal: Deal,
    buyer: Buyer,
) -> None:
    """
    Placeholder notification system.
    For now it logs the match.
    Later we plug in email / SMS / Stripe gating.
    """

    print(
        f"[NOTIFY] Buyer {buyer.email} matched to deal {deal.title} (${deal.price})"
    )

    # Future:
    # - send email
    # - send SMS
    # - trigger webhook
    # - check subscription tier
