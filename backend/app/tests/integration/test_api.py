import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_categories(client):
    response = await client.get("/api/v1/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert len(data["categories"]) >= 8


@pytest.mark.asyncio
async def test_search_crud(client, mock_telegram_user):
    with patch(
        "app.api.v1.auth.verify_telegram_init_data",
        return_value=mock_telegram_user,
    ):
        auth = await client.post(
            "/api/v1/auth/telegram",
            json={"init_data": "test"},
        )
    token = auth.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create = await client.post(
        "/api/v1/searches",
        json={
            "city": "moscow",
            "category": "phones",
            "brands": ["Apple"],
            "exclusions": [],
            "active": True,
        },
        headers=headers,
    )
    assert create.status_code == 201
    search_id = create.json()["id"]

    listing = await client.get("/api/v1/searches", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()) >= 1

    await client.delete(f"/api/v1/searches/{search_id}", headers=headers)
