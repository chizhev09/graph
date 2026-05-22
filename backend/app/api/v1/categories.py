import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()
DATA_DIR = Path(__file__).resolve().parents[3] / "data"


@router.get("")
async def get_categories():
    path = DATA_DIR / "categories.json"
    if not path.exists():
        return {
            "categories": [],
            "exclusions": [],
            "brands_by_category": {},
            "cities": [],
            "sources": [],
        }
    return json.loads(path.read_text(encoding="utf-8"))
