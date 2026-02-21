from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.deal import Deal
from app.services.rentcast_ingest import pull_deals
from app.services.buyer_blast import blast_green_deals

router = APIRouter(prefix="/autonomous", tags=["autonomous"])


@router.post("/run")
async def run_system(db: AsyncSession = Depends(get_db)):

    # 1️⃣ Pull new deals
    pulled = await pull_deals(db)

    # 2️⃣ Get green deals
    res = await db.execute(
        select(Deal).where(Deal.profit_flag == "green")
    )
    greens = list(res.scalars().all())

    # 3️⃣ Blast to buyers
    blasted_total = 0
    for deal in greens:
        blasted_total += await blast_green_deals(db, deal)

    return {
        "pulled": pulled,
        "greens_found": len(greens),
        "buyer_matches_sent": blasted_total,
    }
