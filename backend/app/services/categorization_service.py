import json
import re
from pathlib import Path

from rapidfuzz import fuzz, process

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class CategorizationService:
    def __init__(self) -> None:
        self._categories: dict = {}
        self._taxonomy: dict = {}
        self._load()

    def _load(self) -> None:
        categories_path = DATA_DIR / "categories.json"
        if categories_path.exists():
            self._categories = json.loads(categories_path.read_text(encoding="utf-8"))
        taxonomy_path = DATA_DIR / "taxonomy" / "models.json"
        if taxonomy_path.exists():
            self._taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))

    def _normalize(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
        return re.sub(r"\s+", " ", text).strip()

    def categorize(self, title: str, description: str | None = None) -> dict:
        combined = self._normalize(f"{title} {description or ''}")
        result = {
            "category": None,
            "subcategory": None,
            "brand": None,
            "model": None,
        }

        brands_by_category = self._categories.get("brands_by_category", {})
        categories = [c["id"] for c in self._categories.get("categories", [])]

        best_category = None
        best_score = 0
        for cat_id in categories:
            cat_labels = [cat_id] + [
                c["label"].lower()
                for c in self._categories.get("categories", [])
                if c["id"] == cat_id
            ]
            for label in cat_labels:
                if label in combined:
                    best_category = cat_id
                    best_score = 100
                    break
            if best_category:
                break

        if not best_category and categories:
            match = process.extractOne(
                combined, categories, scorer=fuzz.partial_ratio
            )
            if match and match[1] >= 60:
                best_category = match[0]

        result["category"] = best_category

        if best_category and best_category in brands_by_category:
            brands = brands_by_category[best_category]
            brand_match = process.extractOne(
                combined,
                [b.lower() for b in brands],
                scorer=fuzz.partial_ratio,
            )
            if brand_match and brand_match[1] >= 70:
                idx = [b.lower() for b in brands].index(brand_match[0])
                result["brand"] = brands[idx].lower().replace(" ", "_")

        models = self._taxonomy.get(best_category or "", [])
        if models:
            model_names = [m["slug"] for m in models]
            model_labels = [m["label"] for m in models]
            model_match = process.extractOne(
                combined, model_labels, scorer=fuzz.partial_ratio
            )
            if model_match and model_match[1] >= 75:
                idx = model_labels.index(model_match[0])
                result["model"] = model_names[idx]
                result["subcategory"] = models[idx].get("subcategory")

        return result
