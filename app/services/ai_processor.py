from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.models.buyer import Buyer
from app.services.notifier import send_email
from app.services.monetization import enforce_match_limit


async def process_deal(db: AsyncSession, deal: Deal):
    """
    Main AI processing pipeline:
    - Calculate expected profit
    - Score deal
    - Decide action
    - Match buyer
    - Enforce monetization
    - Update lifecycle
    - Send notification
    """

    # ----------------------------
    # 1️⃣ Calculate expected profit
    # ----------------------------
    if deal.arv and deal.repairs:
        deal.expected_profit = deal.arv - deal.price - deal.repairs
    else:
        deal.expected_profit = 0.0

    # ----------------------------
    # 2️⃣ AI Scoring Logic
    # ----------------------------
    if deal.expected_profit >= 30000:
        deal.score = 95
        deal.ai_decision = "match_buyer"
    elif deal.expected_profit >= 15000:
        deal.score = 80
        deal.ai_decision = "match_buyer"
    elif deal.expected_profit >= 5000:
        deal.score = 60
        deal.ai_decision = "review"
    else:
        deal.score = 30
        deal.ai_decision = "reject"

    # ----------------------------
    # 3️⃣ Decision Handling
    # ----------------------------
    if deal.ai_decision == "match_buyer":

        result = await db.execute(
            select(Buyer)
            .where(
                Buyer.asset_type == deal.asset_type,
                Buyer.city == deal.city,
                Buyer.max_budget >= deal.price,
                Buyer.is_active == True
            )
            .order_by(Buyer.tier.desc())  # prioritize higher tier
        )

        buyer = result.scalars().first()

        if buyer:

            # ----------------------------
            # Monetization enforcement
            # ----------------------------
            enforce_match_limit(buyer)

            # ----------------------------
            # Match deal
            # ----------------------------
            deal.matched_buyer_id = buyer.id
            deal.status = "matched"
            deal.ai_processed_at = datetime.now(timezone.utc)

            # Update buyer stats
            buyer.total_matches = (buyer.total_matches or 0) + 1

            # ----------------------------
            # Send notification email
            # ----------------------------
            await send_email(
                to_email=buyer.email,
                subject="🔥 New Deal Matched",
                html_content=f"""
                    <h2>New Deal Matched</h2>
                    <p><strong>{deal.title}</strong></p>
                    <p>City: {deal.city}</p>
                    <p>Price: ${deal.price}</p>
                    <p>Expected Profit: ${deal.expected_profit}</p>
                """
            )

        else:
            deal.status = "no_match"

    elif deal.ai_decision == "review":
        deal.status = "review"

    else:
        deal.status = "rejected"

    # ----------------------------
    # Final update timestamp
    # ----------------------------
    deal.updated_at = datetime.now(timezone.utc)

    return {
        "deal_id": deal.id,
        "status": deal.status,
        "score": deal.score,
        "decision": deal.ai_decision,
        "expected_profit": deal.expected_profit
    }
