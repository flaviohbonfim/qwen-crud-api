import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.user import User


class TestUserCreateSchema:
    def test_valid_create(self):
        data = UserCreate(name="John", email="john@example.com", password="Password123")
        assert data.name == "John"
        assert data.email == "john@example.com"
        assert data.is_active is True

    def test_password_missing_lowercase(self):
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(name="John", email="john@example.com", password="PASSWORD123")
        errors = exc_info.value.errors()
        assert any("minúscula" in str(e["msg"]).lower() or "lowercase" in str(e["msg"]).lower() for e in errors)

    def test_password_missing_uppercase(self):
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(name="John", email="john@example.com", password="password123")
        errors = exc_info.value.errors()
        assert any("maiúscula" in str(e["msg"]).lower() or "uppercase" in str(e["msg"]).lower() for e in errors)

    def test_password_missing_digit(self):
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(name="John", email="john@example.com", password="Password")
        errors = exc_info.value.errors()
        assert any("dígito" in str(e["msg"]) or "digit" in str(e["msg"]).lower() for e in errors)

    def test_password_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(name="John", email="john@example.com", password="Ab1")

    def test_password_too_long(self):
        with pytest.raises(ValidationError):
            UserCreate(name="John", email="john@example.com", password="A" * 129)

    def test_name_too_long(self):
        with pytest.raises(ValidationError):
            UserCreate(name="A" * 101, email="john@example.com", password="Password123")

    def test_name_empty(self):
        with pytest.raises(ValidationError):
            UserCreate(name="", email="john@example.com", password="Password123")

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            UserCreate(name="John", email="not-an-email", password="Password123")

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            UserCreate(email="john@example.com", password="Password123")

    def test_missing_email(self):
        with pytest.raises(ValidationError):
            UserCreate(name="John", password="Password123")

    def test_missing_password(self):
        with pytest.raises(ValidationError):
            UserCreate(name="John", email="john@example.com")


class TestUserUpdateSchema:
    def test_valid_update_partial(self):
        data = UserUpdate(name="Jane")
        assert data.name == "Jane"
        assert data.email is None

    def test_valid_update_all_fields(self):
        data = UserUpdate(
            name="Jane",
            email="jane@example.com",
            is_active=False,
            password="NewPass123",
        )
        assert data.name == "Jane"
        assert data.is_active is False
        assert data.password == "NewPass123"

    def test_password_validation_in_update(self):
        with pytest.raises(ValidationError):
            UserUpdate(password="weak")

    def test_password_too_short_in_update(self):
        with pytest.raises(ValidationError):
            UserUpdate(password="Ab1")

    def test_all_none(self):
        data = UserUpdate()
        assert data.name is None
        assert data.email is None
        assert data.is_active is None
        assert data.password is None


class TestUserResponseSchema:
    def test_from_attributes(self):
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            name="John",
            email="john@example.com",
            hashed_password="hash",
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )

        response = UserResponse.model_validate(user)
        assert response.id == user_id
        assert response.name == "John"
        assert response.email == "john@example.com"
        assert response.is_active is True
        assert response.created_at is not None
