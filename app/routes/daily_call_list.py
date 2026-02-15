# app/routes/daily_call_list.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.daily_call_list_sender import send_daily_call_list

router = APIRouter()

@router.post("/daily/call-list/send")
async def send_call_list(top: int = 10, db: AsyncSession = Depends(get_db)):
    return await send_daily_call_list(db, top=top)
