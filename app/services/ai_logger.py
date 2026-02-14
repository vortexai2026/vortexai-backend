from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ai_decision_log import AIDecisionLog


async def log_ai_decision(
    db: AsyncSession,
    deal_id: int | None,
    buyer_id: int | None,
    decision: str | None,
    status: str | None,
    score: float | None,
    expected_profit: float | None,
    error: str | None = None,
):
    row = AIDecisionLog(
        deal_id=deal_id,
        buyer_id=buyer_id,
        decision=decision,
        status=status,
        score=score,
        expected_profit=expected_profit,
        error=error,
    )
    db.add(row)
