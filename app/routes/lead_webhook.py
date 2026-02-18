import os
from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.lead_flow import ingest_webhook, ingest_csv_bytes

router = APIRouter(prefix="/leads", tags=["Leads"])

@router.post("/webhook")
async def lead_webhook(payload: dict, db: AsyncSession = Depends(get_db), x_lead_token: str | None = Header(default=None)):
    expected = os.getenv("LEAD_WEBHOOK_TOKEN", "")
    if expected and x_lead_token != expected:
        raise HTTPException(status_code=401, detail="Bad webhook token")
    deal = await ingest_webhook(db, payload)
    return {"ok": True, "deal_id": deal.id}

@router.post("/csv")
async def lead_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    deals = await ingest_csv_bytes(db, await file.read())
    return {"ok": True, "count": len(deals)}
