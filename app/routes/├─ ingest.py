from fastapi import APIRouter

# Define a router for ingest routes
router = APIRouter()

@router.get("/health")
def ingest_health():
    return {"ok": True, "service": "ingest"}

