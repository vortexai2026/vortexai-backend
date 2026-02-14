from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.metrics_engine import get_operator_metrics

router = APIRouter()

@router.get("/operator/metrics")
async def operator_metrics(db: AsyncSession = Depends(get_db)):
    metrics = await get_operator_metrics(db)
    return metrics
