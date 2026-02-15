from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.followup import FollowUp

router = APIRouter()

@router.post("/deals/{deal_id}/schedule_followup")
async def schedule_followup(
    deal_id: int,
    note: str,
    due_date: date,
    db: AsyncSession = Depends(get_db)
):
    followup = FollowUp(
        deal_id=deal_id,
        note=note,
        due_date=due_date
    )

    db.add(followup)
    await db.commit()
    await db.refresh(followup)

    return {"message": "Follow-up scheduled"}


@router.get("/followups/today")
async def get_today_followups(db: AsyncSession = Depends(get_db)):
    today = date.today()

    result = await db.execute(
        select(FollowUp).where(
            FollowUp.due_date <= today,
            FollowUp.completed == False
        )
    )

    items = result.scalars().all()

    return {
        "count": len(items),
        "items": [
            {
                "id": f.id,
                "deal_id": f.deal_id,
                "note": f.note,
                "due_date": f.due_date
            }
            for f in items
        ]
    }


@router.post("/followups/{followup_id}/complete")
async def complete_followup(followup_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(FollowUp).where(FollowUp.id == followup_id)
    )

    followup = result.scalar_one_or_none()

    if followup:
        followup.completed = True
        await db.commit()

    return {"message": "Follow-up completed"}
