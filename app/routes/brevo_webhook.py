import os
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.car import CarLead, CarMessage

router = APIRouter(prefix="/webhooks/brevo", tags=["Brevo Webhooks"])
SECRET = os.getenv("BREVO_WEBHOOK_SECRET", "")

@router.post("/sms")
async def brevo_sms_webhook(req: Request, db: AsyncSession = Depends(get_db)):
    body = await req.json()

    # OPTIONAL: verify secret if you configure it in Brevo
    # token = req.headers.get("x-webhook-secret")
    # if SECRET and token != SECRET:
    #     raise HTTPException(401, "Invalid webhook secret")

    # You must map Brevo payload fields to:
    # inbound phone + message text
    # Brevo payload varies by event type, so we store raw for now.
    inbound_phone = body.get("from") or body.get("sender") or body.get("phone")
    inbound_text = body.get("text") or body.get("content") or body.get("message")

    if not inbound_phone or not inbound_text:
        return {"ok": True, "note": "No inbound message fields found", "raw": body}

    # Find lead by phone
    res = await db.execute(select(CarLead).where(CarLead.phone == inbound_phone))
    lead = res.scalar_one_or_none()
    if not lead:
        return {"ok": True, "note": "Lead not found for phone", "phone": inbound_phone}

    db.add(CarMessage(lead_id=lead.id, direction="inbound", message=inbound_text))
    await db.commit()
    return {"ok": True}
