# app/routes/autonomous.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.deal import Deal
from app.services.rentcast_ingest import pull_deals
from app.services.daily_report import send_green_report
from app.services.buyer_blast import blast_green_deals

router = APIRouter(prefix="/autonomous", tags=["autonomous"])


@router.post("/run")
async def run_system(db: AsyncSession = Depends(get_db)):
    """
    Runs the full 'Level 7' cycle:
    1) Pull deals from RentCast into DB
    2) Send green deals report to your personal email
    3) Blast each green deal to matching buyers
    """
    pulled = await pull_deals(db)

    # pull greens after ingest
    res = await db.execute(select(Deal).where(Deal.profit_flag == "green"))
    greens = list(res.scalars().all())

    blasted_total = 0
    for deal in greens:
        blasted_total += await blast_green_deals(db, deal)

    green_report_sent = await send_green_report(db)

    return {
        "pulled": pulled,
        "greens_found": len(greens),
        "buyer_emails_sent": blasted_total,
        "green_report_sent": green_report_sent,
    }
