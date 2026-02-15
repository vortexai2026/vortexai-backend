# app/routes/negotiation.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.negotiation_engine import generate_negotiation_plan

router = APIRouter()

@router.get("/deals/{deal_id}/negotiation")
async def get_negotiation_plan(
    deal_id: int,
    assignment_fee: float = 15000,
    db: AsyncSession = Depends(get_db)
):
    try:
        out = await generate_negotiation_plan(db, deal_id=deal_id, assignment_fee=float(assignment_fee))
        return {
            "deal_id": deal_id,
            "recommended_offer": out.recommended_offer,
            "max_offer": out.max_offer,
            "strategy": out.strategy,
            "script": out.script,
            "reasoning": out.reasoning
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
