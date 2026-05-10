import uuid

import pytest
from httpx import AsyncClient


class TestCreateUser:
    async def test_create_user_success(self, api_client: AsyncClient, user_data: dict):
        response = await api_client.post("/users/", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == user_data["name"]
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "created_at" in data
        assert data["is_active"] is True

    async def test_create_user_duplicate_email(self, api_client: AsyncClient, user_data: dict):
        await api_client.post("/users/", json=user_data)
        response = await api_client.post("/users/", json=user_data)
        assert response.status_code == 409
        assert "e-mail" in response.json()["detail"].lower() or "email" in response.json()["detail"].lower()

    async def test_create_user_invalid_password(self, api_client: AsyncClient):
        invalid_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "invalid",
        }
        response = await api_client.post("/users/", json=invalid_data)
        assert response.status_code == 422

    async def test_create_user_invalid_email(self, api_client: AsyncClient):
        invalid_data = {
            "name": "Test User",
            "email": "not-an-email",
            "password": "Password123",
        }
        response = await api_client.post("/users/", json=invalid_data)
        assert response.status_code == 422

    async def test_create_user_short_password(self, api_client: AsyncClient):
        invalid_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "Ab1",
        }
        response = await api_client.post("/users/", json=invalid_data)
        assert response.status_code == 422


class TestListUsers:
    async def test_list_users_success(self, api_client: AsyncClient, user_data: dict):
        await api_client.post("/users/", json=user_data)
        response = await api_client.get("/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["email"] == user_data["email"]

    async def test_list_users_empty(self, api_client: AsyncClient):
        response = await api_client.get("/users/")
        assert response.status_code == 404

    async def test_list_users_multiple(self, api_client: AsyncClient, user_data: dict):
        await api_client.post("/users/", json=user_data)
        second_user = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "Password456",
        }
        await api_client.post("/users/", json=second_user)
        response = await api_client.get("/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestGetUser:
    async def test_get_user_success(self, api_client: AsyncClient, user_data: dict):
        create_response = await api_client.post("/users/", json=user_data)
        user_id = create_response.json()["id"]
        response = await api_client.get(f"/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]

    async def test_get_user_not_found(self, api_client: AsyncClient):
        response = await api_client.get(f"/users/{uuid.uuid4()}")
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"].lower() or "not found" in response.json()["detail"].lower()


class TestUpdateUser:
    async def test_update_user_success(self, api_client: AsyncClient, user_data: dict):
        create_response = await api_client.post("/users/", json=user_data)
        user_id = create_response.json()["id"]
        update_data = {"name": "Jane Doe"}
        response = await api_client.patch(f"/users/{user_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane Doe"
        assert data["email"] == user_data["email"]

    async def test_update_user_not_found(self, api_client: AsyncClient):
        response = await api_client.patch(f"/users/{uuid.uuid4()}", json={"name": "Test"})
        assert response.status_code == 404

    async def test_update_user_duplicate_email(self, api_client: AsyncClient, user_data: dict):
        await api_client.post("/users/", json=user_data)
        create_response = await api_client.post("/users/", json={
            "name": "Other User",
            "email": "other@example.com",
            "password": "Password123",
        })
        user_id = create_response.json()["id"]
        response = await api_client.patch(f"/users/{user_id}", json={"email": user_data["email"]})
        assert response.status_code == 409

    async def test_update_user_partial_fields(self, api_client: AsyncClient, user_data: dict):
        create_response = await api_client.post("/users/", json=user_data)
        user_id = create_response.json()["id"]
        update_data = {"is_active": False}
        response = await api_client.patch(f"/users/{user_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert data["name"] == user_data["name"]

    async def test_update_user_password(self, api_client: AsyncClient, user_data: dict):
        create_response = await api_client.post("/users/", json=user_data)
        user_id = create_response.json()["id"]
        update_data = {"password": "NewPassword456"}
        response = await api_client.patch(f"/users/{user_id}", json=update_data)
        assert response.status_code == 200


class TestDeleteUser:
    async def test_delete_user_success(self, api_client: AsyncClient, user_data: dict):
        create_response = await api_client.post("/users/", json=user_data)
        user_id = create_response.json()["id"]
        response = await api_client.delete(f"/users/{user_id}")
        assert response.status_code == 204

    async def test_delete_user_not_found(self, api_client: AsyncClient):
        response = await api_client.delete(f"/users/{uuid.uuid4()}")
        assert response.status_code == 404

    async def test_delete_user_then_get(self, api_client: AsyncClient, user_data: dict):
        create_response = await api_client.post("/users/", json=user_data)
        user_id = create_response.json()["id"]
        await api_client.delete(f"/users/{user_id}")
        response = await api_client.get(f"/users/{user_id}")
        assert response.status_code == 404


class TestHealthCheck:
    async def test_health_check(self, api_client: AsyncClient):
        response = await api_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
