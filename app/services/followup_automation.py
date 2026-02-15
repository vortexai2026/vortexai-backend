# app/services/followup_automation.py

from datetime import datetime, timedelta, date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.models.followup import FollowUp
from app.models.buyer_outreach_log import BuyerOutreachLog

# SETTINGS
AUTO_CONTACT_DELAY_HOURS = 48
STALE_ESCALATION_HOURS = 72
REBLAST_AFTER_HOURS = 24


# =========================
# 1️⃣ AUTO FOLLOW-UP CREATOR
# =========================

async def auto_generate_followups(db: AsyncSession):

    now = datetime.utcnow()
    threshold = now - timedelta(hours=AUTO_CONTACT_DELAY_HOURS)

    q = select(Deal).where(
        Deal.status == "CONTACTED",
        Deal.last_contacted_at != None,
        Deal.last_contacted_at <= threshold
    )

    res = await db.execute(q)
    deals = res.scalars().all()

    created = 0

    for d in deals:

        # Check if active follow-up already exists
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
            note="AUTO: Seller not contacted in 48 hours",
            due_date=date.today()
        )

        db.add(new_followup)
        created += 1

    await db.commit()

    return {
        "auto_followups_created": created
    }


# =========================
# 2️⃣ STALE DEAL ESCALATION
# =========================

async def escalate_stale_deals(db: AsyncSession):

    now = datetime.utcnow()
    threshold = now - timedelta(hours=STALE_ESCALATION_HOURS)

    q = select(Deal).where(
        Deal.status.in_(["GREEN", "CONTACTED"]),
        Deal.last_contacted_at != None,
        Deal.last_contacted_at <= threshold
    )

    res = await db.execute(q)
    deals = res.scalars().all()

    escalated = 0

    for d in deals:
        if d.priority_score is None:
            continue

        d.priority_score += 15
        d.priority_reason = (d.priority_reason or "") + " | stale_escalation"
        escalated += 1

    await db.commit()

    return {
        "stale_escalated": escalated
    }


# =========================
# 3️⃣ AUTO REBLAST (Optional)
# =========================

async def auto_reblast_offers(db: AsyncSession):

    now = datetime.utcnow()
    threshold = now - timedelta(hours=REBLAST_AFTER_HOURS)

    # Deals with offer sent but no recent outreach
    q = select(Deal).where(
        Deal.status == "OFFER_SENT",
        Deal.offer_sent_at != None,
        Deal.offer_sent_at <= threshold
    )

    res = await db.execute(q)
    deals = res.scalars().all()

    reblast_candidates = 0

    for d in deals:

        # Check if recent outreach already happened
        outreach_q = select(func.count()).select_from(BuyerOutreachLog).where(
            BuyerOutreachLog.deal_id == d.id,
            BuyerOutreachLog.sent_at >= threshold
        )

        outreach_count = await db.scalar(outreach_q)

        if outreach_count and outreach_count > 0:
            continue

        # Escalate priority instead of blasting automatically
        if d.priority_score:
            d.priority_score += 20
            d.priority_reason = (d.priority_reason or "") + " | reblast_needed"

        reblast_candidates += 1

    await db.commit()

    return {
        "reblast_flagged": reblast_candidates
    }


# =========================
# 4️⃣ MASTER AUTOMATION RUN
# =========================

async def run_followup_automation(db: AsyncSession):

    followups = await auto_generate_followups(db)
    stale = await escalate_stale_deals(db)
    reblast = await auto_reblast_offers(db)

    return {
        "followups": followups,
        "stale": stale,
        "reblast": reblast
    }
