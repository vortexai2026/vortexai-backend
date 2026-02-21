# app/routes/autonomous.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.deal import Deal
from app.services.daily_report import send_daily_green_report
from app.services.rentcast_ingest import pull_all_markets

router = APIRouter(prefix="/autonomous", tags=["Autonomous"])


@router.post("/run")
async def run_autonomous(db: AsyncSession = Depends(get_db)):
    # 1) Pull deals from RentCast + score
    pull_result = await pull_all_markets(db, total_target=50)

    # 2) Count flags
    res = await db.execute(select(Deal.profit_flag))
    flags = [x[0] for x in res.all() if x[0]]
    scored_total = len(flags)
    scored_green = sum(1 for f in flags if f == "green")
    scored_orange = sum(1 for f in flags if f == "orange")
    scored_red = sum(1 for f in flags if f == "red")

    # 3) Email report (greens)
    daily_email_sent_count = await send_daily_green_report(db)

    return {
        "pull": pull_result,
        "scored_total": scored_total,
        "scored_green": scored_green,
        "scored_orange": scored_orange,
        "scored_red": scored_red,
        "daily_email_sent_count": daily_email_sent_count,
    }
