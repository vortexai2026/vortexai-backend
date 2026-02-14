from fastapi import APIRouter

router = APIRouter(prefix="/ingest", tags=["Ingest"])

@router.post("/")
async def ingest_data(data: dict):
    return {"message": "Data ingested", "data": data}
