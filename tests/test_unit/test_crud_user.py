import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.crud.user import user_crud
from app.models.user import User


@pytest.fixture
def mock_db() -> MagicMock:
    db = MagicMock()
    db.execute = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.delete = AsyncMock()
    return db


@pytest.fixture
def sample_user() -> User:
    return User(
        id=uuid.uuid4(),
        name="John Doe",
        email="john@example.com",
        hashed_password="hashed_password_123",
        is_active=True,
    )


def _make_mock_result(scalar_value=None, scalar_list=None):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = scalar_value
    if scalar_list is not None:
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = scalar_list
        mock_result.scalars.return_value = mock_scalars
    return mock_result


class TestUserCRUDGetById:
    async def test_returns_user_when_found(self, mock_db, sample_user):
        mock_db.execute.return_value = _make_mock_result(scalar_value=sample_user)

        result = await user_crud.get_by_id(mock_db, sample_user.id)

        assert result == sample_user
        mock_db.execute.assert_called_once()

    async def test_returns_none_when_not_found(self, mock_db):
        mock_db.execute.return_value = _make_mock_result(scalar_value=None)

        result = await user_crud.get_by_id(mock_db, uuid.uuid4())

        assert result is None


class TestUserCRUDGetByEmail:
    @pytest.mark.parametrize("email,expected", [
        pytest.param("john@example.com", True, id="existing-email"),
        pytest.param("nonexistent@example.com", False, id="not-found"),
    ])
    async def test_get_by_email(self, mock_db, sample_user, email, expected):
        if expected:
            mock_db.execute.return_value = _make_mock_result(scalar_value=sample_user)
        else:
            mock_db.execute.return_value = _make_mock_result(scalar_value=None)

        result = await user_crud.get_by_email(mock_db, email)

        if expected:
            assert result == sample_user
        else:
            assert result is None


class TestUserCRUDGetAll:
    @pytest.mark.parametrize("skip,limit,expected_count", [
        pytest.param(0, 10, 3, id="default-range"),
        pytest.param(1, 1, 1, id="pagination-skip-1"),
        pytest.param(0, 0, 0, id="zero-limit"),
    ])
    async def test_get_all(self, mock_db, sample_user, skip, limit, expected_count):
        users = [sample_user] * expected_count
        mock_db.execute.return_value = _make_mock_result(scalar_list=users)

        result = await user_crud.get_all(mock_db, skip=skip, limit=limit)

        assert len(result) == expected_count

    async def test_get_all_returns_empty_list(self, mock_db):
        mock_db.execute.return_value = _make_mock_result(scalar_list=[])

        result = await user_crud.get_all(mock_db)

        assert result == []


class TestUserCRUDCreate:
    async def test_creates_user(self, mock_db, sample_user):
        user_data = {
            "id": sample_user.id,
            "name": sample_user.name,
            "email": sample_user.email,
            "hashed_password": sample_user.hashed_password,
        }

        result = await user_crud.create(mock_db, user_data)

        assert result == sample_user
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    async def test_creates_user_with_uuid(self, mock_db):
        user_id = uuid.uuid4()
        user_data = {
            "id": user_id,
            "name": "Test User",
            "email": "test@example.com",
            "hashed_password": "hashed_secret",
        }

        result = await user_crud.create(mock_db, user_data)

        assert result.id == user_id
        mock_db.add.assert_called_once()


class TestUserCRUDUpdate:
    @pytest.mark.parametrize("field,value", [
        pytest.param("name", "New Name", id="name"),
        pytest.param("email", "new@example.com", id="email"),
        pytest.param("is_active", False, id="is_active"),
    ])
    async def test_updates_field(self, mock_db, sample_user, field, value):
        user_data = {field: value}

        result = await user_crud.update(mock_db, sample_user, user_data)

        assert getattr(result, field) == value
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    async def test_updates_multiple_fields(self, mock_db, sample_user):
        user_data = {
            "name": "Updated Name",
            "email": "updated@example.com",
            "is_active": False,
        }

        result = await user_crud.update(mock_db, sample_user, user_data)

        assert result.name == "Updated Name"
        assert result.email == "updated@example.com"
        assert result.is_active is False

    async def test_updates_only_non_none_fields(self, mock_db, sample_user):
        original_name = sample_user.name
        user_data = {"name": None, "email": "new@example.com"}

        result = await user_crud.update(mock_db, sample_user, user_data)

        assert result.email == "new@example.com"
        assert result.name == original_name


class TestUserCRUDDelete:
    async def test_deletes_user(self, mock_db, sample_user):
        await user_crud.delete(mock_db, sample_user)

        mock_db.delete.assert_called_once_with(sample_user)
        mock_db.commit.assert_called_once()
