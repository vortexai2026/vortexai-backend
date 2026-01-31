import os
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.database import fetch_one
from app.pdf_generator import generate_pdf

router = APIRouter(prefix="/pdf", tags=["pdf"])

@router.post("/generate/{deal_id}")
def generate_pdf_for_deal(deal_id: str):
    # Validate uuid
    try:
        uuid.UUID(deal_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid deal_id UUID")

    deal = fetch_one("SELECT * FROM deals WHERE id=%s", (deal_id,))
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    # only generate if good enough
    ai_score = int(deal.get("ai_score") or 0)
    if ai_score and ai_score < 50:
        raise HTTPException(status_code=400, detail="Deal too low score for PDF")

    out_path = f"/tmp/vortexai_{deal_id}.pdf"
    generate_pdf(deal, out_path)
    return FileResponse(out_path, media_type="application/pdf", filename=f"deal_{deal_id}.pdf")
