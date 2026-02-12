# app/routes/ingest.py
from fastapi import APIRouter
router = APIRouter(tags=["Ingest"])

@router.get("/")
async def ingest_root():
    return {"ok": True, "message": "Ingest root"}
