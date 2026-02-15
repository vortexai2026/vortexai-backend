# app/routes/autonomous.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.execution_pipeline import run_autonomous_cycle

router = APIRouter()

@router.post("/autonomous/run")
async def autonomous_run(limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await run_autonomous_cycle(db, limit=limit)
