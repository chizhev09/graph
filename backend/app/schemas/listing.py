from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ListingResponse(BaseModel):
    id: int
    source: str
    external_id: str
    title: str
    description: str | None
    price: Decimal | None
    city: str | None
    url: str
    images: list[str]
    category: str | None
    subcategory: str | None
    brand: str | None
    model: str | None
    published_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
