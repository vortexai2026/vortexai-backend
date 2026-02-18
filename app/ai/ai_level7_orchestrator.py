from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.deal import Deal
from app.services.comps_engine import enrich_deal_with_arv
from app.services.offer_engine import generate_offer
from app.services.buyer_blast_engine import blast_buyers
from app.services.seller_sms_brevo import kickoff_sms
from app.services.lifecycle_control import set_status


async def process_once(db: AsyncSession):
    # 1️⃣ NEW deals → ARV → SCORED
    new_deals = (await db.execute(
        select(Deal).where(Deal.status == "NEW")
    )).scalars().all()

    for deal in new_deals:
        await enrich_deal_with_arv(deal)
        await set_status(db, deal, "SCORED")

    # 2️⃣ SCORED → CONTACT SELLER
    scored = (await db.execute(
        select(Deal).where(Deal.status == "SCORED")
    )).scalars().all()

    for deal in scored:
        await kickoff_sms(db, deal)

    # 3️⃣ NEGOTIATING → GENERATE OFFER
    negotiating = (await db.execute(
        select(Deal).where(Deal.status == "NEGOTIATING")
    )).scalars().all()

    for deal in negotiating:
        await generate_offer(db, deal)

    # 4️⃣ UNDER CONTRACT → BLAST BUYERS
    under_contract = (await db.execute(
        select(Deal).where(Deal.status == "UNDER_CONTRACT")
    )).scalars().all()

    for deal in under_contract:
        await blast_buyers(db, deal)

    return {"cycle": "complete"}
