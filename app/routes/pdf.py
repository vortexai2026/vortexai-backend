# app/routes/pdf.py
from fastapi import APIRouter
router = APIRouter(tags=["PDF"])

@router.post("/pdf/generate/{deal_id}")
async def generate_pdf(deal_id: int):
    return {"ok": True, "pdf_url": f"/pdfs/deal_{deal_id}.pdf"}
