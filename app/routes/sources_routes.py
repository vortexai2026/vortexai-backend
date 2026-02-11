from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter(prefix="/sources", tags=["sources"])
SOURCES_PATH = Path("app/data/sources.json")

@router.get("/")
def get_sources():
    with open(SOURCES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/{category}")
def get_sources_by_category(category: str):
    with open(SOURCES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(category, [])
