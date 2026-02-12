from fastapi import APIRouter

router = APIRouter(tags=["pdf"])

@router.post("/pdf/generate/{deal_id}")
def generate_pdf(deal_id: int):
    return {"deal_id": deal_id, "pdf_url": "https://example.com/generated.pdf"}
