# app/services/execution_pipeline.py

import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.services.ai_scoring import score_deal
from app.services.buyer_blast_engine import match_buyers_for_deal, build_buyer_email
from app.models.buyer_outreach_log import BuyerOutreachLog
from app.services.emailer import send_email

AUTO_BLAST_LIMIT = int(os.getenv("AUTO_BLAST_LIMIT", "25"))
AUTO_BLAST_DRY_RUN = os.getenv("AUTO_BLAST_DRY_RUN", "true").lower() == "true"
AUTO_BLAST_MIN_SCORE = float(os.getenv("AUTO_BLAST_MIN_SCORE", "20"))

async def process_one_deal(db: AsyncSession, deal: Deal) -> dict:
    """
    Runs: score -> (NEW or GREEN) -> if GREEN, blast buyers -> log outreach
    """
    # Score + set status NEW/GREEN
    deal = score_deal(deal)

    # Persist scoring changes
    await db.commit()
    await db.refresh(deal)

    result = {
        "deal_id": deal.id,
        "status": deal.status,
        "score": deal.score,
        "buyers_matched": 0,
        "sent": 0,
        "failed": 0,
        "dry_run": AUTO_BLAST_DRY_RUN
    }

    # Only blast if GREEN and score threshold met
    if deal.status != "GREEN":
        return result

    if deal.score is None or float(deal.score) < AUTO_BLAST_MIN_SCORE:
        return result

    buyers = await match_buyers_for_deal(db, deal, limit=AUTO_BLAST_LIMIT)
    result["buyers_matched"] = len(buyers)

    if not buyers:
        return result

    subject, body = build_buyer_email(deal, assignment_fee=float(getattr(deal, "assignment_fee", None) or 15000))

    sent = 0
    failed = 0

    for b in buyers:
        email = getattr(b, "email", None)
        if not email:
            continue

        log = BuyerOutreachLog(
            deal_id=deal.id,
            buyer_id=b.id,
            channel="email",
            subject=subject,
            body=body,
            status="SENT",
            error=None
        )

        if not AUTO_BLAST_DRY_RUN:
            try:
                send_email(email, subject, body)
                sent += 1
            except Exception as e:
                log.status = "FAILED"
                log.error = str(e)
                failed += 1
        else:
            # dry run: pretend sent, but still log
            sent += 1

        db.add(log)

    await db.commit()

    result["sent"] = sent
    result["failed"] = failed
    return result


async def run_autonomous_cycle(db: AsyncSession, limit: int = 10) -> dict:
    """
    Pulls NEW deals, scores them, blasts buyers for GREEN deals.
    """
    q = (
        select(Deal)
        .where(Deal.status == "NEW")
        .order_by(Deal.id.desc())
        .limit(limit)
    )
    res = await db.execute(q)
    deals = res.scalars().all()

    processed = []
    for d in deals:
        processed.append(await process_one_deal(db, d))

    return {
        "pulled_new": len(deals),
        "processed": processed
    }
