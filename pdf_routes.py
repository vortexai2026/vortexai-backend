import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from app.pdf_generator import generate_pdf  # ✅ correct import

DATABASE_URL = os.getenv("DATABASE_URL")

router = APIRouter(prefix="/pdf", tags=["pdf"])

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@router.post("/generate/{deal_id}")
def generate_pdf_for_deal(deal_id: str):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM deals WHERE id=%s", (deal_id,))
        deal = cur.fetchone()
        cur.close()

        if not deal:
            return JSONResponse(
                status_code=404,
                content={"error": "Deal not found"}
            )

        if (deal.get("ai_score") or 0) < 75:
            return JSONResponse(
                status_code=400,
                content={"error": "Deal is not GREEN enough for PDF generation"}
            )

        pdf_path = generate_pdf(deal)
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"deal_{deal_id}.pdf"
        )

    finally:
        conn.close()

