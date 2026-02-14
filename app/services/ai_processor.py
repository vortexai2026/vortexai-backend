from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.models.buyer import Buyer
from app.services.notifier import send_email


async def process_deal(db: AsyncSession, deal: Deal):

    # 1️⃣ Calculate expected profit
    if deal.arv and deal.repairs:
        deal.expected_profit = deal.arv - deal.price - deal.repairs
    else:
        deal.expected_profit = 0.0

    # 2️⃣ Simple AI scoring logic
    if deal.expected_profit and deal.expected_profit > 20000:
        deal.score = 90
        deal.ai_decision = "match_buyer"
    elif deal.expected_profit and deal.expected_profit > 10000:
        deal.score = 70
        deal.ai_decision = "review"
    else:
        deal.score = 40
        deal.ai_decision = "reject"

    # 3️⃣ If AI says match → find buyer
    if deal.ai_decision == "match_buyer":

        result = await db.execute(
            select(Buyer)
            .where(
                Buyer.asset_type == deal.asset_type,
                Buyer.city == deal.city,
                Buyer.max_budget >= deal.price,
                Buyer.is_active == True
            )
            .order_by(Buyer.tier.desc())
        )

        buyer = result.scalars().first()

        if buyer:
            deal.matched_buyer_id = buyer.id
            deal.status = "matched"
            deal.ai_processed_at = datetime.now(timezone.utc)

            # Increase buyer match counter
            buyer.total_matches = (buyer.total_matches or 0) + 1

            # ✅ Send email notification
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
    else:
        deal.status = "rejected"

    deal.updated_at = datetime.now(timezone.utc)

    return {
        "deal_id": deal.id,
        "status": deal.status,
        "score": deal.score,
        "decision": deal.ai_decision
    }
