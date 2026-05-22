from app.utils.hashing import listing_hash, normalize_text


def test_normalize_text():
    assert normalize_text("  Hello   World  ") == "hello world"


def test_listing_hash_stable():
    h1 = listing_hash("avito", "123", "iPhone 15", "50000")
    h2 = listing_hash("avito", "123", "iPhone 15", "50000")
    assert h1 == h2
    h3 = listing_hash("avito", "124", "iPhone 15", "50000")
    assert h1 != h3
