import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/sources", tags=["sources"])

SOURCES_PATH = Path("app/data/sources.json")


@router.get("/")
def get_sources():
    if not SOURCES_PATH.exists():
        raise HTTPException(status_code=500, detail="sources.json not found")

    with SOURCES_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/{category}")
def get_sources_by_category(category: str):
    if not SOURCES_PATH.exists():
        raise HTTPException(status_code=500, detail="sources.json not found")

    with SOURCES_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get(category, [])
