from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class SearchCreate(BaseModel):
    city: str
    category: str | None = None
    brands: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    keywords: str | None = None
    exclude_keywords: str | None = None
    condition: str | None = None
    source_types: list[str] = Field(default_factory=list)
    active: bool = True


class SearchUpdate(BaseModel):
    city: str | None = None
    category: str | None = None
    brands: list[str] | None = None
    exclusions: list[str] | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    keywords: str | None = None
    exclude_keywords: str | None = None
    condition: str | None = None
    source_types: list[str] | None = None
    active: bool | None = None


class SearchResponse(BaseModel):
    id: int
    user_id: int
    city: str
    category: str | None
    brands: list[str]
    exclusions: list[str]
    min_price: Decimal | None
    max_price: Decimal | None
    keywords: str | None
    exclude_keywords: str | None
    condition: str | None
    source_types: list[str]
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
