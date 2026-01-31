import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.database import fetch_one
from app.pdf_generator import generate_pdf

router = APIRouter(prefix="/pdf", tags=["pdf"])

@router.post("/generate/{deal_id}")
def generate_pdf_for_deal(deal_id: str):
    deal = fetch_one("SELECT * FROM deals WHERE id=%s", (deal_id,))
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    file_path = f"/tmp/{uuid.uuid4()}.pdf"
    generate_pdf(deal, file_path)

    return FileResponse(file_path, media_type="application/pdf")
