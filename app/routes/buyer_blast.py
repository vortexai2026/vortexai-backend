from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.deal import Deal
from app.models.buyer import Buyer
from app.models.buyer_outreach_log import BuyerOutreachLog
from app.services.buyer_blast_engine import match_buyers_for_deal, build_buyer_email
from app.services.emailer import send_email

router = APIRouter()

@router.post("/deals/{deal_id}/blast_buyers")
async def blast_buyers(
    deal_id: int,
    limit: int = 30,
    assignment_fee: float = 15000,
    dry_run: bool = False,
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = res.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    buyers = await match_buyers_for_deal(db, deal, limit=limit)

    if not buyers:
        return {"message": "No matching buyers found", "sent": 0}

    subject, body = build_buyer_email(deal, assignment_fee=assignment_fee)

    sent = 0
    failures = 0

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

        if not dry_run:
            try:
                send_email(email, subject, body)
                sent += 1
            except Exception as e:
                log.status = "FAILED"
                log.error = str(e)
                failures += 1
        else:
            sent += 1

        db.add(log)

    await db.commit()

    return {
        "message": "Buyer blast complete",
        "matched_buyers": len(buyers),
        "sent": sent,
        "failed": failures,
        "dry_run": dry_run
    }
