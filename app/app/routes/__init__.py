from fastapi import APIRouter
from app.ai_universal_ingest import ingest_post

router = APIRouter(prefix="/ingest", tags=["Ingest"])

@router.post("/")
def ingest(payload: dict):
    return ingest_post(
        source_name=payload["source"],
        category=payload["category"],
        raw_text=payload["text"]
    )
