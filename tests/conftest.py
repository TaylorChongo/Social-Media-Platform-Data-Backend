import uuid

import pytest

from app.actions import create_user


@pytest.fixture
def make_user():
    """Give tests a function that creates a new user with a random name."""

    def _make_user():
        name = "test_" + uuid.uuid4().hex[:8]
        return create_user(name, name + "@mail.com")

    return _make_user
