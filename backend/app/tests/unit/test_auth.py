import pytest
from unittest.mock import patch

from app.integrations.telegram.auth import verify_telegram_init_data


def test_verify_invalid_init_data():
    assert verify_telegram_init_data("", "token") is None
    assert verify_telegram_init_data("invalid", "token") is None


@pytest.mark.asyncio
async def test_auth_telegram_endpoint(client, mock_telegram_user):
    with patch(
        "app.api.v1.auth.verify_telegram_init_data",
        return_value=mock_telegram_user,
    ):
        response = await client.post(
            "/api/v1/auth/telegram",
            json={"init_data": "test_init_data"},
        )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
