# app/routes/ingest.py
from fastapi import APIRouter

router = APIRouter(tags=["ingest"])

# Example endpoint
@router.get("/")
def ingest_root():
    return {"message": "Ingest route is ready"}
