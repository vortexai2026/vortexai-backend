# app/routes/offer_letter.py

import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.deal import Deal
from app.models.offer_log import OfferLog
from app.services.negotiation_engine import generate_negotiation_plan
from app.services.offer_letter_engine import build_offer_email, build_offer_letter_text
from app.services.emailer import send_email

router = APIRouter()

@router.post("/deals/{deal_id}/send_offer_letter")
async def send_offer_letter(
    deal_id: int,
    seller_email: str,
    assignment_fee: float = 15000,
    dry_run: bool = False,
    db: AsyncSession = Depends(get_db)
):
    # Load deal
    res = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = res.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    # Generate negotiation plan
    plan = await generate_negotiation_plan(db, deal_id=deal_id, assignment_fee=float(assignment_fee))
    offer_price = float(plan.recommended_offer)

    subject, body = build_offer_email(deal, offer_price)
    offer_letter = build_offer_letter_text(deal, offer_price)

    log = OfferLog(
        deal_id=deal.id,
        offer_price=offer_price,
        channel="email",
        recipient=seller_email,
        subject=subject,
        body=body,
        status="SENT",
        error=None
    )

    if not dry_run:
        try:
            send_email(seller_email, subject, body)
        except Exception as e:
            log.status = "FAILED"
            log.error = str(e)

    db.add(log)

    # Update deal fields
    deal.offer_sent_price = offer_price
    deal.offer_sent_at = datetime.utcnow()
    deal.offer_status = "SENT"
    deal.status = "OFFER_SENT"

    await db.commit()
    await db.refresh(deal)

    return {
        "message": "Offer letter processed",
        "dry_run": dry_run,
        "offer_price": offer_price,
        "email_subject": subject,
        "email_body": body,
        "offer_letter_text": offer_letter,
        "deal_status": deal.status
    }
