# app/routes/ingest.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.ingest import IngestPayload
from app.services.ingest_engine import ingest_batch


router = APIRouter(tags=["Ingest"])


@router.get("/")
async def ingest_root():
    return {"message": "Ingest is ready. POST /ingest/ with { deals: [...] }"}


@router.post("/ingest/")
async def ingest_data(payload: IngestPayload, db: AsyncSession = Depends(get_db)):
    # converts pydantic objects to dict for engine
    deals = [d.model_dump() for d in payload.deals]
    return await ingest_batch(db, deals)
