import os
import re
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.brevo_client import brevo_post
from app.models.deal import Deal
from app.models.seller_call import SellerCall  # you already have this; we reuse it as message log


HELP = {"HELP", "INFO"}
STOP = {"STOP", "CANCEL", "END", "QUIT", "UNSUBSCRIBE"}
START = {"START", "YES", "UNSTOP"}

def _kw(s: str) -> str:
    t = (s or "").strip().upper()
    t = re.sub(r"[^A-Z]", "", t)
    return t

def is_stop(text: str) -> bool: return _kw(text) in STOP
def is_help(text: str) -> bool: return _kw(text) in HELP
def is_start(text: str) -> bool: return _kw(text) in START

def now():
    return datetime.now(timezone.utc)

def seller_msg_1(deal: Deal) -> str:
    tail = os.getenv("BREVO_REPLY_INSTRUCTIONS", "").strip()
    base = f"Hi — is this the owner of {deal.address}? Are you open to a quick cash offer? Reply YES/NO."
    return f"{base} {tail}".strip()

def seller_msg_2(deal: Deal) -> str:
    tail = os.getenv("BREVO_REPLY_INSTRUCTIONS", "").strip()
    base = "Quick questions: 1) condition/repairs? 2) timeline? 3) best price you'd take?"
    return f"{base} {tail}".strip()

async def _send_sms(number_e164: str, text: str) -> dict:
    # Brevo transactional SMS send endpoint (docs show /v3/transactionalSMS/send) :contentReference[oaicite:6]{index=6}
    payload = {
        "sender": os.getenv("BREVO_SMS_SENDER", "VORTEXAI"),
        "recipient": number_e164,
        "content": text,
        "type": os.getenv("BREVO_SMS_TYPE", "transactional"),
    }
    return await brevo_post("/transactionalSMS/send", payload)

async def _log(db: AsyncSession, deal_id: Optional[int], phone: str, direction: str, text: str, meta: Optional[Dict[str, Any]] = None):
    rec = SellerCall(
        deal_id=deal_id,
        phone=phone,
        direction=direction,  # "OUT" / "IN"
        message=text,
        created_at=now(),
        meta=meta or {},
    )
    db.add(rec)
    await db.commit()

async def _has_opted_out(db: AsyncSession, phone: str) -> bool:
    rows = (await db.execute(
        select(SellerCall).where(SellerCall.phone == phone).order_by(SellerCall.created_at.desc()).limit(200)
    )).scalars().all()
    return any((r.meta or {}).get("opt_out") is True for r in rows)

async def _mark_opt_out(db: AsyncSession, phone: str):
    await _log(db, None, phone, "IN", "OPTOUT", {"opt_out": True})

async def kickoff_sms(db: AsyncSession, deal: Deal) -> None:
    phone = (getattr(deal, "seller_phone", "") or "").strip()
    if not phone:
        return
    if await _has_opted_out(db, phone):
        return

    msg = seller_msg_1(deal)
    resp = await _send_sms(phone, msg)
    await _log(db, deal.id, phone, "OUT", msg, {"brevo": resp})

    deal.status = "CONTACTED"
    await db.commit()

async def handle_inbound(db: AsyncSession, from_number: str, body: str) -> dict:
    phone = (from_number or "").strip()

    # Basic STOP/HELP/START handling per Brevo guidance :contentReference[oaicite:7]{index=7}
    if is_stop(body):
        await _mark_opt_out(db, phone)
        return {"action": "OPTED_OUT"}

    # Find most recent deal for this phone (adjust if you link differently)
    deal = (await db.execute(
        select(Deal).where(Deal.seller_phone == phone).order_by(Deal.created_at.desc())
    )).scalars().first()

    await _log(db, deal.id if deal else None, phone, "IN", body)

    if not deal:
        return {"action": "UNMATCHED"}

    txt = (body or "").strip().upper()
    if txt in {"YES", "Y"}:
        deal.status = "NEGOTIATING"
        await db.commit()

        msg = seller_msg_2(deal)
        resp = await _send_sms(phone, msg)
        await _log(db, deal.id, phone, "OUT", msg, {"brevo": resp})
        return {"action": "QUALIFYING_SENT"}

    if txt in {"NO", "N"}:
        deal.status = "DEAD"
        await db.commit()
        return {"action": "NOT_INTERESTED"}

    deal.status = "NEGOTIATING"
    await db.commit()
    return {"action": "LOGGED"}
