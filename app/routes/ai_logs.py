from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.ai_decision_log import AIDecisionLog

router = APIRouter(tags=["AI Logs"])


@router.get("/admin/ai_logs")
async def list_ai_logs(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AIDecisionLog)
        .order_by(AIDecisionLog.created_at.desc())
        .limit(limit)
    )

    rows = result.scalars().all()

    return [
        {
            "id": r.id,
            "deal_id": r.deal_id,
            "buyer_id": r.buyer_id,
            "decision": r.decision,
            "status": r.status,
            "score": r.score,
            "expected_profit": r.expected_profit,
            "error": r.error,
            "created_at": r.created_at,
        }
        for r in rows
    ]
