from fastapi import APIRouter

router = APIRouter(tags=["sources"])

@router.get("/sources/")
def get_sources():
    return {"sources": []}

@router.get("/sources/{category}")
def get_sources_by_category(category: str):
    return {"category": category, "sources": []}
