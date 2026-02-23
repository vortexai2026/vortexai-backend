from pydantic import BaseModel
from typing import Optional

class DealEvaluateIn(BaseModel):
    arv: Optional[float] = None
    repairs: Optional[float] = 0
    assignment_fee_target: Optional[float] = 10000
    investor_discount: Optional[float] = 0.70  # 70% rule

class DealEvaluateOut(BaseModel):
    deal_id: int
    arv: float
    repairs: float
    mao: float
    offer_price: float
    estimated_spread: float
    confidence: int
