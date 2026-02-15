# app/routes/stripe_webhook.py

import os
import stripe
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.deal import Deal

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if not webhook_secret:
        raise HTTPException(status_code=500, detail="STRIPE_WEBHOOK_SECRET missing")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            webhook_secret
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

    # Handle checkout completion
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        deal_id = session.get("metadata", {}).get("deal_id")
        amou
