import hashlib
import re


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def listing_hash(
    source: str, external_id: str, title: str, price: str | None = None
) -> str:
    payload = f"{source}:{external_id}:{normalize_text(title)}:{price or ''}"
    return hashlib.sha256(payload.encode()).hexdigest()
