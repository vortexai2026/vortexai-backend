# app/services/ai_processor.py
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.models.buyer import Buyer
from app.services.notifier import send_email
from app.services.monetization import enforce_match_limit
from app.services.ai_logger import log_ai_decision
from app.services.ai_scoring import score_deal


async def process_deal(db: AsyncSession, deal: Deal):
    buyer = None

    try:
        # -------------------------
        # 1) Score deal (real scoring engine)
        # -------------------------
        score = await score_deal(db, deal)

        # Store score + decision on deal
        deal.score = float(score.ai_score)
        deal.ai_decision = score.decision

        # Compute expected profit if needed (score_deal may compute best-effort)
        # Keep it stored for admin/profit visibility
        if getattr(deal, "expected_profit", None) is None or float(getattr(deal, "expected_profit", 0) or 0) == 0:
            # best-effort: try calculate from fields
            arv = float(getattr(deal, "arv", 0) or 0)
            price = float(getattr(deal, "price", 0) or 0)
            repairs = float(getattr(deal, "repairs", 0) or 0)
            if arv > 0 and price > 0:
                deal.expected_profit = arv - price - repairs
            else:
                deal.expected_profit = float(getattr(deal, "expected_profit", 0) or 0)

        # -------------------------
        # 2) Decision -> matching
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
                .order_by(Buyer.tier.desc(), Buyer.max_budget.desc())
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
                        <p>Asset Type: {deal.asset_type}</p>
                        <p>Price: ${deal.price}</p>
                        <p>Expected Profit: ${deal.expected_profit}</p>
                        <p>AI Score: {deal.score} / 100</p>
                        <p>Confidence: {score.confidence:.0f}%</p>
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
        # 3) Log success (audit)
        # -------------------------
        await log_ai_decision(
            db=db,
            deal_id=deal.id,
            buyer_id=(buyer.id if buyer else None),
            decision=f"{deal.ai_decision}|score={deal.score:.1f}|conf={score.confidence:.0f}",
            status=deal.status,
            score=float(deal.score or 0),
            expected_profit=float(getattr(deal, "expected_profit", 0) or 0),
            error=None,
        )

        return {
            "deal_id": deal.id,
            "status": deal.status,
            "score": deal.score,
            "decision": deal.ai_decision,
            "confidence": score.confidence,
            "expected_profit": getattr(deal, "expected_profit", 0),
            "components": {
                "profit": score.profit_score,
                "risk": score.risk_score,
                "demand": score.demand_score,
                "liquidity": score.liquidity_score,
                "urgency": score.urgency_score,
            },
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
