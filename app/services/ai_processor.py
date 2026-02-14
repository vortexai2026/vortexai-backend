from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.models.buyer import Buyer
from app.services.notifier import send_email
from app.services.monetization import enforce_match_limit
from app.services.ai_logger import log_ai_decision


async def process_deal(db: AsyncSession, deal: Deal):
    buyer = None

    try:
        # -------------------------
        # 1️⃣ Expected Profit
        # -------------------------
        if deal.arv is not None and deal.repairs is not None:
            deal.expected_profit = float(deal.arv) - float(deal.price) - float(deal.repairs)
        else:
            deal.expected_profit = 0.0

        # -------------------------
        # 2️⃣ Scoring Logic
        # -------------------------
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

        # -------------------------
        # 3️⃣ Buyer Matching
        # -------------------------
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
                enforce_match_limit(buyer)

                deal.matched_buyer_id = buyer.id
                deal.status = "matched"
                deal.ai_processed_at = datetime.now(timezone.utc)

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

        deal.updated_at = datetime.now(timezone.utc)

        # -------------------------
        # 4️⃣ Log Success
        # -------------------------
        await log_ai_decision(
            db=db,
            deal_id=deal.id,
            buyer_id=(buyer.id if buyer else None),
            decision=deal.ai_decision,
            status=deal.status,
            score=float(deal.score or 0),
            expected_profit=float(deal.expected_profit or 0),
            error=None,
        )

        return {
            "deal_id": deal.id,
            "status": deal.status,
            "score": deal.score,
            "decision": deal.ai_decision,
            "expected_profit": deal.expected_profit,
        }

    except Exception as e:
        error_message = str(e)

        deal.status = "failed"
        deal.updated_at = datetime.now(timezone.utc)

        await log_ai_decision(
            db=db,
            deal_id=getattr(deal, "id", None),
            buyer_id=(buyer.id if buyer else None),
            decision=getattr(deal, "ai_decision", None),
            status="failed",
            score=float(getattr(deal, "score", 0) or 0),
            expected_profit=float(getattr(deal, "expected_profit", 0) or 0),
            error=error_message,
        )

        raise
