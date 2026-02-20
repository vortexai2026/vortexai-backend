from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.database import get_db
from app.models.deal import Deal
from app.services.scoring import score_deal
from app.services.daily_report import send_daily_green_report
from app.services.deal_blast import blast_deal_to_buyers

router = APIRouter(prefix="/autonomous", tags=["Autonomous"])

@router.post("/run")
async def autonomous_run(db: AsyncSession = Depends(get_db)):
    # Score pending deals
    res = await db.execute(
        select(Deal).where(or_(Deal.profit_flag == None, Deal.profit_flag == "")).limit(100)
    )
    pending = list(res.scalars().all())

    scored_green = scored_orange = scored_red = 0

    for d in pending:
        d = score_deal(d)
        if d.profit_flag == "green":
            scored_green += 1
        elif d.profit_flag == "orange":
            scored_orange += 1
        else:
            scored_red += 1

    await db.commit()

    # Send report
    sent_count = await send_daily_green_report(db)

    return {
        "scored_total": len(pending),
        "scored_green": scored_green,
        "scored_orange": scored_orange,
        "scored_red": scored_red,
        "daily_email_sent_count": sent_count,
    }

@router.post("/blast/{deal_id}")
async def blast_one(deal_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = res.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    if deal.profit_flag != "green":
        raise HTTPException(status_code=400, detail="Only green deals can be blasted")
    result = await blast_deal_to_buyers(db, deal)
    return {"message": "Blast complete", "result": result}
