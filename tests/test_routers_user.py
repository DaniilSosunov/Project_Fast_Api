import pytest
import json
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user(client):
    user_data = {
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lo1l@kek.com",
    }

    # Получаем экземпляр AsyncClient из фикстуры
    async for ac in client: # Используем async for, но только один раз
        resp = await ac.post("/user/", json=user_data)  # Передаем данные как json
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == user_data["name"]
        assert data["surname"] == user_data["surname"]
        assert data["email"] == user_data["email"]
        break # выходим из цикла после первого прохода
