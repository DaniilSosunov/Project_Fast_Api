import pytest


@pytest.mark.asyncio
async def test_create_user(client):
    """Тест создания пользователя с синхронным клиентом"""
    test_user = {
        "name": "Test",
        "surname": "User",
        "email": "test@example.com"
    }

    # Синхронный вызов через TestClient
    response = client.post("/user", json=test_user)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]