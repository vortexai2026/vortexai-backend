# app/services/followup_automation.py

from datetime import datetime, timedelta, date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.models.followup import FollowUp

AUTO_CONTACT_DELAY_HOURS = 48

async def auto_generate_followups(db: AsyncSession):

    now = datetime.utcnow()
    threshold = now - timedelta(hours=AUTO_CONTACT_DELAY_HOURS)

    # Deals that were contacted but have no followup
    q = select(Deal).where(
        Deal.status == "CONTACTED",
        Deal.last_contacted_at != None,
        Deal.last_contacted_at <= threshold
    )

    res = await db.execute(q)
    deals = res.scalars().all()

    created = 0

    for d in deals:
        # Check if already has pending followup
        existing_q = select(FollowUp).where(
            FollowUp.deal_id == d.id,
            FollowUp.completed == False
        )
        existing_res = await db.execute(existing_q)
        existing = existing_res.scalar_one_or_none()

        if existing:
            continue

        new_followup = FollowUp(
            deal_id=d.id,
            note="Auto-generated follow-up: Seller not contacted in 48h",
            due_date=date.today()
        )

        db.add(new_followup)
        created += 1

    await db.commit()

    return {"auto_followups_created": created}
