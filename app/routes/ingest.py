from fastapi import APIRouter

router = APIRouter(tags=["ingest"])

@router.get("/")
def ingest_root():
    return {"message": "Ingest route is ready"}
