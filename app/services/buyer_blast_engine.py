from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

# Temporary placeholder logic until we build real AI matching

async def match_buyers_for_deal(db: AsyncSession, deal) -> List[dict]:
    """
    Returns list of matched buyers.
    For now: returns empty list (safe startup).
    """
    return []


def build_buyer_email(deal, buyer) -> str:
    """
    Builds simple buyer email body.
    """
    return f"""
New Deal Available!

Title: {deal.title}
Location: {deal.location}
Price: {deal.price}

Visit platform to review.
"""
