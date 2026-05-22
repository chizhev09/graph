#!/usr/bin/env python3
"""Sync categories from frontend filter-data.ts to backend/data/categories.json."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILTER_DATA = ROOT / "frontend" / "src" / "components" / "pages" / "main" / "filter-data.ts"
CITIES_DATA = ROOT / "frontend" / "src" / "components" / "pages" / "main" / "cities-data.ts"
SOURCES_DATA = ROOT / "frontend" / "src" / "components" / "pages" / "main" / "sources-data.ts"
OUTPUT = ROOT / "backend" / "data" / "categories.json"


def extract_array_block(content: str, name: str) -> str:
    pattern = rf"export const {name}(?:\s*:\s*[^=]+)?\s*=\s*(\[[\s\S]*?\n\])"
    match = re.search(pattern, content)
    return match.group(1) if match else "[]"


def parse_categories(content: str) -> list[dict]:
    block = extract_array_block(content, "CATEGORIES")
    items = []
    for m in re.finditer(
        r"\{\s*id:\s*'([^']+)',\s*emoji:\s*'([^']*)',\s*label:\s*'([^']*)'\s*\}",
        block,
    ):
        items.append({"id": m.group(1), "emoji": m.group(2), "label": m.group(3)})
    return items


def parse_exclusions(content: str) -> list[dict]:
    block = extract_array_block(content, "EXCLUSIONS")
    items = []
    for m in re.finditer(
        r"\{\s*id:\s*'([^']+)',\s*emoji:\s*'([^']*)',\s*label:\s*'([^']*)'\s*\}",
        block,
    ):
        items.append({"id": m.group(1), "emoji": m.group(2), "label": m.group(3)})
    return items


def parse_sources(content: str) -> list[dict]:
    block = extract_array_block(content, "SOURCES")
    items = []
    for m in re.finditer(
        r"\{\s*id:\s*'([^']+)',\s*label:\s*'([^']*)'\s*\}",
        block,
    ):
        items.append({"id": m.group(1), "label": m.group(2)})
    return items


def parse_cities(content: str) -> list[dict]:
    block = extract_array_block(content, "CITIES")
    items = []
    for m in re.finditer(
        r"\{\s*id:\s*'([^']+)',\s*label:\s*'([^']*)'\s*\}",
        block,
    ):
        items.append({"id": m.group(1), "label": m.group(2)})
    return items


def parse_brands(content: str) -> dict:
    block_match = re.search(
        r"export const BRANDS_BY_CATEGORY[^=]*=\s*(\{[\s\S]*?\n\})",
        content,
    )
    if not block_match:
        return {}
    block = block_match.group(1)
    brands: dict = {}
    for cat_match in re.finditer(r"'([^']+)':\s*\[([^\]]*)\]", block):
        cat_id = cat_match.group(1)
        brands_raw = cat_match.group(2)
        brand_list = re.findall(r"'([^']+)'", brands_raw)
        brands[cat_id] = brand_list
    return brands


def main() -> None:
    if not FILTER_DATA.exists():
        raise SystemExit(f"filter-data.ts not found: {FILTER_DATA}")
    content = FILTER_DATA.read_text(encoding="utf-8")
    cities_content = CITIES_DATA.read_text(encoding="utf-8") if CITIES_DATA.exists() else content
    sources_content = SOURCES_DATA.read_text(encoding="utf-8") if SOURCES_DATA.exists() else content
    data = {
        "categories": parse_categories(content),
        "exclusions": parse_exclusions(content),
        "cities": parse_cities(cities_content),
        "sources": parse_sources(sources_content),
        "brands_by_category": parse_brands(content),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Synced to {OUTPUT}")
    print(
        f"  categories: {len(data['categories'])}, "
        f"cities: {len(data['cities'])}, "
        f"sources: {len(data['sources'])}, "
        f"exclusions: {len(data['exclusions'])}"
    )


if __name__ == "__main__":
    main()
