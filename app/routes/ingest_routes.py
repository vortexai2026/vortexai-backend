from fastapi import APIRouter, HTTPException
from app.services.ingest import ingest_source

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/{source_name}")
def ingest(source_name: str):
    try:
        count = ingest_source(source_name)
        return {"ok": True, "source": source_name, "ingested": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
