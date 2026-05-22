from app.services.categorization_service import CategorizationService


def test_categorize_iphone():
    service = CategorizationService()
    result = service.categorize("iPhone 15 Pro Max 256GB", "Продаю iPhone 15 Pro Max")
    assert result["category"] == "phones"
    assert result.get("brand") is not None or result.get("model") is not None
