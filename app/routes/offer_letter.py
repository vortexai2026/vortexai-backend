# app/routes/offer_letter.py

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.deal import Deal
from app.models.offer_log import OfferLog
from app.services.negotiation_engine import generate_negotiation_plan
from app.services.offer_letter_engine import build_offer_email, build_offer_letter_text
from app.services.pdf_offer_pack import generate_offer_pdf_bytes, save_offer_pdf
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

    # Negotiation plan => recommended offer
    plan = await generate_negotiation_plan(db, deal_id=deal_id, assignment_fee=float(assignment_fee))
    offer_price = float(plan.recommended_offer)

    subject, body = build_offer_email(deal, offer_price)
    offer_letter_text = build_offer_letter_text(deal, offer_price)

    # Build PDF
    terms = """- Purchase AS-IS
- Cash or private funds
- Closing timeline: 7–21 days (or faster if needed)
- Subject to clear title and standard closing process
"""
    pdf_bytes = generate_offer_pdf_bytes(
        deal_title=deal.title or "Property",
        deal_city=deal.city or "",
        offer_price=offer_price,
        terms_text=terms
    )
    pdf_path = save_offer_pdf(deal.id, pdf_bytes)

    # Log offer
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

    # Send email + attachment
    if not dry_run:
        try:
            send_email(
                seller_email,
                subject,
                body,
                attachments=[(f"Offer_Deal_{deal.id}.pdf", pdf_bytes, "application/pdf")]
            )
        except Exception as e:
            log.status = "FAILED"
            log.error = str(e)

    db.add(log)

    # Update deal fields
    deal.offer_sent_price = offer_price
    deal.offer_sent_at = datetime.utcnow()
    deal.offer_status = "SENT"
    deal.status = "OFFER_SENT"
    deal.offer_pdf_path = pdf_path
    deal.offer_pdf_url = None  # later if you upload to storage/S3

    await db.commit()
    await db.refresh(deal)

    return {
        "message": "Offer email + PDF processed",
        "dry_run": dry_run,
        "offer_price": offer_price,
        "deal_status": deal.status,
        "pdf_path": pdf_path
    }
