# app/schemas/ingest.py
from pydantic import BaseModel, Field
from typing import Optional, List


class IngestDealIn(BaseModel):
    title: str
    asset_type: str
    city: str
    price: float

    # optional enrichment
    arv: Optional[float] = None
    repairs: Optional[float] = None
    assignment_fee: Optional[float] = None

    # optional source metadata (we store in decision log only if your Deal model doesn't have fields)
    source: Optional[str] = None
    source_url: Optional[str] = None
    external_id: Optional[str] = None


class IngestPayload(BaseModel):
    deals: List[IngestDealIn] = Field(default_factory=list)
