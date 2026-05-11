import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api.routers.users import (
    _hash_password,
    create_user,
    delete_user,
    get_user,
    list_users,
    update_user,
)
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User


def _make_user(user_id=None, name="John", email="john@example.com", hashed_password="hash", is_active=True, created_at=None):
    return User(
        id=user_id or uuid.uuid4(),
        name=name,
        email=email,
        hashed_password=hashed_password,
        is_active=is_active,
        created_at=created_at or datetime.now(timezone.utc),
    )


class TestHashPassword:
    def test_returns_hex_string(self):
        result = _hash_password("test")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_deterministic(self):
        assert _hash_password("same") == _hash_password("same")

    def test_different_inputs_different_hashes(self):
        assert _hash_password("pass1") != _hash_password("pass2")


class TestCreateUserHandler:
    async def test_success(self):
        mock_db = AsyncMock()
        user = _make_user()

        with patch("app.api.routers.users.user_crud") as mock_crud, \
             patch("app.api.routers.users._hash_password", return_value="hash"):
            mock_crud.get_by_email = AsyncMock(return_value=None)
            mock_crud.create = AsyncMock(return_value=user)

            payload = UserCreate(name="John", email="john@example.com", password="Password123")
            result = await create_user(payload, mock_db)

            assert result.id == user.id
            assert result.name == "John"
            mock_crud.get_by_email.assert_called_once()
            mock_crud.create.assert_called_once()

    async def test_duplicate_email_raises_409(self):
        mock_db = AsyncMock()
        existing = _make_user(name="Existing")

        with patch("app.api.routers.users.user_crud") as mock_crud:
            mock_crud.get_by_email = AsyncMock(return_value=existing)

            payload = UserCreate(name="John", email="john@example.com", password="Password123")

            with pytest.raises(HTTPException) as exc_info:
                await create_user(payload, mock_db)

            assert exc_info.value.status_code == 409


class TestListUsersHandler:
    async def test_success(self):
        mock_db = AsyncMock()
        users = [_make_user()]

        with patch("app.api.routers.users.user_crud") as mock_crud:
            mock_crud.get_all = AsyncMock(return_value=users)

            result = await list_users(mock_db)

            assert len(result) == 1
            assert result[0].name == "John"

    async def test_empty_raises_404(self):
        mock_db = AsyncMock()

        with patch("app.api.routers.users.user_crud") as mock_crud:
            mock_crud.get_all = AsyncMock(return_value=[])

            with pytest.raises(HTTPException) as exc_info:
                await list_users(mock_db)

            assert exc_info.value.status_code == 404


class TestGetUserHandler:
    async def test_success(self):
        mock_db = AsyncMock()
        user = _make_user()

        with patch("app.api.routers.users.user_crud") as mock_crud:
            mock_crud.get_by_id = AsyncMock(return_value=user)

            result = await get_user(user.id, mock_db)

            assert result.id == user.id

    async def test_not_found_raises_404(self):
        mock_db = AsyncMock()
        user_id = uuid.uuid4()

        with patch("app.api.routers.users.user_crud") as mock_crud:
            mock_crud.get_by_id = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await get_user(user_id, mock_db)

            assert exc_info.value.status_code == 404


class TestUpdateUserHandler:
    async def test_success_name_only(self):
        mock_db = AsyncMock()
        user = _make_user()
        updated = _make_user(name="Jane")

        with patch("app.api.routers.users.user_crud") as mock_crud, \
             patch("app.api.routers.users._hash_password", return_value="hash"):
            mock_crud.get_by_id = AsyncMock(return_value=user)
            mock_crud.get_by_email = AsyncMock(return_value=None)
            mock_crud.update = AsyncMock(return_value=updated)

            payload = UserUpdate(name="Jane")
            result = await update_user(user.id, payload, mock_db)

            assert result.name == "Jane"

    async def test_success_email_same_user(self):
        mock_db = AsyncMock()
        user = _make_user()
        updated = _make_user(email="new@example.com")

        with patch("app.api.routers.users.user_crud") as mock_crud, \
             patch("app.api.routers.users._hash_password", return_value="hash"):
            mock_crud.get_by_id = AsyncMock(return_value=user)
            mock_crud.get_by_email = AsyncMock(return_value=None)
            mock_crud.update = AsyncMock(return_value=updated)

            payload = UserUpdate(email="new@example.com")
            result = await update_user(user.id, payload, mock_db)

            assert result.email == "new@example.com"

    async def test_not_found_raises_404(self):
        mock_db = AsyncMock()
        user_id = uuid.uuid4()

        with patch("app.api.routers.users.user_crud") as mock_crud:
            mock_crud.get_by_id = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await update_user(user_id, UserUpdate(name="Jane"), mock_db)

            assert exc_info.value.status_code == 404

    async def test_duplicate_email_raises_409(self):
        mock_db = AsyncMock()
        user = _make_user()
        other = _make_user(user_id=uuid.uuid4(), name="Jane")

        with patch("app.api.routers.users.user_crud") as mock_crud:
            mock_crud.get_by_id = AsyncMock(return_value=user)
            mock_crud.get_by_email = AsyncMock(return_value=other)

            with pytest.raises(HTTPException) as exc_info:
                await update_user(user.id, UserUpdate(email="jane@example.com"), mock_db)

            assert exc_info.value.status_code == 409

    async def test_password_hashed_on_update(self):
        mock_db = AsyncMock()
        user = _make_user()
        updated = _make_user(hashed_password="newhash")

        with patch("app.api.routers.users.user_crud") as mock_crud, \
             patch("app.api.routers.users._hash_password", return_value="newhash") as mock_hash:
            mock_crud.get_by_id = AsyncMock(return_value=user)
            mock_crud.get_by_email = AsyncMock(return_value=None)
            mock_crud.update = AsyncMock(return_value=updated)

            payload = UserUpdate(password="NewPassword123")
            await update_user(user.id, payload, mock_db)

            mock_hash.assert_called_once_with("NewPassword123")

    async def test_none_password_excluded_from_update(self):
        mock_db = AsyncMock()
        user = _make_user()
        updated = _make_user(name="Jane")

        with patch("app.api.routers.users.user_crud") as mock_crud, \
             patch("app.api.routers.users._hash_password") as mock_hash:
            mock_crud.get_by_id = AsyncMock(return_value=user)
            mock_crud.get_by_email = AsyncMock(return_value=None)
            mock_crud.update = AsyncMock(return_value=updated)

            payload = UserUpdate(name="Jane")
            await update_user(user.id, payload, mock_db)

            mock_hash.assert_not_called()

    async def test_explicit_none_password_deletes_key(self):
        mock_db = AsyncMock()
        user = _make_user()
        updated = _make_user(name="Jane")

        with patch("app.api.routers.users.user_crud") as mock_crud, \
             patch("app.api.routers.users._hash_password") as mock_hash:
            mock_crud.get_by_id = AsyncMock(return_value=user)
            mock_crud.get_by_email = AsyncMock(return_value=None)
            mock_crud.update = AsyncMock(return_value=updated)

            payload = UserUpdate(name="Jane", password=None)
            await update_user(user.id, payload, mock_db)

            mock_hash.assert_not_called()


class TestDeleteUserHandler:
    async def test_success(self):
        mock_db = AsyncMock()
        user = _make_user()

        with patch("app.api.routers.users.user_crud") as mock_crud:
            mock_crud.get_by_id = AsyncMock(return_value=user)
            mock_crud.delete = AsyncMock()

            await delete_user(user.id, mock_db)

            mock_crud.get_by_id.assert_called_once()
            mock_crud.delete.assert_called_once()

    async def test_not_found_raises_404(self):
        mock_db = AsyncMock()
        user_id = uuid.uuid4()

        with patch("app.api.routers.users.user_crud") as mock_crud:
            mock_crud.get_by_id = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await delete_user(user_id, mock_db)

            assert exc_info.value.status_code == 404
