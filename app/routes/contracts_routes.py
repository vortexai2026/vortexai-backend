import uuid
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.database import execute, fetch_one
from app.services.contract_generator import generate_contract_pdf

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.post("/draft/{deal_id}")
def create_contract_draft(deal_id: str, payload: dict):
    draft_id = str(uuid.uuid4())

    execute("""
        INSERT INTO contract_drafts (id, deal_id, contract_type, data)
        VALUES (%s,%s,%s,%s::jsonb)
    """, (
        draft_id,
        deal_id,
        payload.get("contract_type", "assignment"),
        json.dumps(payload)
    ))

    return {"ok": True, "draft_id": draft_id}


@router.get("/pdf/{draft_id}")
def get_contract_pdf(draft_id: str):
    row = fetch_one("SELECT * FROM contract_drafts WHERE id=%s", (draft_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Draft not found")

    pdf_path = generate_contract_pdf(row["data"])
    return FileResponse(pdf_path, media_type="application/pdf", filename="contract_draft.pdf")
