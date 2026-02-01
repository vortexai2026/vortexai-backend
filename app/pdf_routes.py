import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.database import fetch_one
from app.pdf_generator import generate_pdf
from io import BytesIO

router = APIRouter(prefix="/pdf", tags=["pdf"])

@router.post("/generate/{deal_id}")
def generate_pdf_for_deal(deal_id: str):
    # Validate UUID
    try:
        uuid.UUID(deal_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid deal_id UUID")

    deal = fetch_one("SELECT * FROM deals WHERE id=%s", (deal_id,))
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    pdf_bytes = generate_pdf(deal)
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=deal_{deal_id}.pdf"}
    )
