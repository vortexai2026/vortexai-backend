from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.seller_call import SellerCall

router = APIRouter()

@router.post("/deals/{deal_id}/log_call")
async def log_call(
    deal_id: int,
    motivation_level: int,
    asking_price: float,
    timeline: str,
    notes: str,
    db: AsyncSession = Depends(get_db)
):
    call = SellerCall(
        deal_id=deal_id,
        motivation_level=motivation_level,
        asking_price=asking_price,
        timeline=timeline,
        notes=notes
    )

    db.add(call)
    await db.commit()
    await db.refresh(call)

    return {"message": "Call logged"}
