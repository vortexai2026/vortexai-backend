from sqlalchemy import select, func
from app.models.deal import Deal

async def get_operator_metrics(db):

    total_deals = await db.scalar(select(func.count()).select_from(Deal))

    green = await db.scalar(
        select(func.count()).where(Deal.status == "GREEN")
    )

    contacted = await db.scalar(
        select(func.count()).where(Deal.status == "CONTACTED")
    )

    offers = await db.scalar(
        select(func.count()).where(Deal.status == "OFFER_SENT")
    )

    under_contract = await db.scalar(
        select(func.count()).where(Deal.status == "UNDER_CONTRACT")
    )

    assigned = await db.scalar(
        select(func.count()).where(Deal.status == "ASSIGNED")
    )

    paid = await db.scalar(
        select(func.count()).where(Deal.stripe_payment_status == "PAID")
    )

    expected_profit = await db.scalar(
        select(func.sum(Deal.assignment_fee))
    ) or 0

    actual_revenue = await db.scalar(
        select(func.sum(Deal.paid_amount))
    ) or 0

    return {
        "total_deals": total_deals,
        "green": green,
        "contacted": contacted,
        "offers_sent": offers,
        "under_contract": under_contract,
        "assigned": assigned,
        "paid": paid,
        "expected_profit": float(expected_profit),
        "actual_revenue": float(actual_revenue),
    }
