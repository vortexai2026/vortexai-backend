# app/routes/contracts.py
from fastapi import APIRouter
from app.db import database as db

router = APIRouter(tags=["Contracts"])

@router.post("/contracts/draft/{deal_id}")
async def create_contract_draft(deal_id: int, content: str):
    query = "INSERT INTO contracts(deal_id, content) VALUES($1, $2) RETURNING id"
    draft = await db.fetch_one(query, deal_id, content)
    return {"ok": True, "draft_id": draft["id"]}

@router.get("/contracts/pdf/{draft_id}")
async def get_contract_pdf(draft_id: int):
    # Placeholder PDF logic
    query = "SELECT * FROM contracts WHERE id=$1"
    draft = await db.fetch_one(query, draft_id)
    return {"ok": True, "pdf_url": f"/pdfs/{draft_id}.pdf"}
