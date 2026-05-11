import uuid

import pytest

from app.models.user import User


class TestUserModel:
    def test_equality_same_id(self):
        user_id = uuid.uuid4()
        user1 = User(
            id=user_id,
            name="John",
            email="john@example.com",
            hashed_password="hash",
        )
        user2 = User(
            id=user_id,
            name="Jane",
            email="jane@example.com",
            hashed_password="hash",
        )
        assert user1 == user2

    def test_inequality_different_id(self):
        user1 = User(
            id=uuid.uuid4(),
            name="John",
            email="john@example.com",
            hashed_password="hash",
        )
        user2 = User(
            id=uuid.uuid4(),
            name="Jane",
            email="jane@example.com",
            hashed_password="hash",
        )
        assert user1 != user2

    def test_inequality_non_user_string(self):
        user = User(
            id=uuid.uuid4(),
            name="John",
            email="john@example.com",
            hashed_password="hash",
        )
        assert user != "not a user"

    def test_inequality_non_user_int(self):
        user = User(
            id=uuid.uuid4(),
            name="John",
            email="john@example.com",
            hashed_password="hash",
        )
        assert user != 123

    def test_inequality_non_user_dict(self):
        user = User(
            id=uuid.uuid4(),
            name="John",
            email="john@example.com",
            hashed_password="hash",
        )
        assert user != {"id": uuid.uuid4()}

    def test_inequality_non_user_none(self):
        user = User(
            id=uuid.uuid4(),
            name="John",
            email="john@example.com",
            hashed_password="hash",
        )
        assert user != None  # noqa: E711
