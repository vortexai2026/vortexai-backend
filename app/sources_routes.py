from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter(prefix="/sources", tags=["Sources"])

SOURCES_PATH = Path("app/data/sources.json")


@router.get("/")
def get_sources():
    if not SOURCES_PATH.exists():
        return {"error": "sources.json not found"}

    with open(SOURCES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/{category}")
def get_sources_by_category(category: str):
    if not SOURCES_PATH.exists():
        return {"error": "sources.json not found"}

    with open(SOURCES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if category not in data:
        return {"error": f"Category '{category}' not found"}

    return data[category]
