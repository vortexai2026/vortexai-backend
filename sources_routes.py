import json
import os
from fastapi import APIRouter

router = APIRouter(prefix="/sources", tags=["sources"])

BASE_DIR = os.path.dirname(__file__)
CONFIG_DIR = os.path.join(BASE_DIR, "config")

def load_json(name):
    path = os.path.join(CONFIG_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("")
def get_sources():
    data = load_json("sources_master.json")
    return data

@router.get("/cities")
def get_cities():
    data = load_json("cities_us_ca.json")
    return data
