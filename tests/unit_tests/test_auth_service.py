from types import SimpleNamespace
from unittest.mock import Mock
import pytest

from app.config.security import verify_password
from app.service.auth_service import AuthService
from app.config.security import hash_password, verify_password


def test_register_creates_user_with_hashed_password():
    user_repository_mock = Mock()
    user_repository_mock.get_by_username.return_value = None

    def create_user(username, password_hash):
        return SimpleNamespace(
            id=1,
            username=username,
            password_hash=password_hash,
        )

    user_repository_mock.create.side_effect = create_user

    auth_service = AuthService(user_repository_mock)

    user = auth_service.register("bogdan", "secret123")

    assert user.username == "bogdan"
    assert user.password_hash != "secret123"
    assert verify_password("secret123", user.password_hash) is True

    user_repository_mock.get_by_username.assert_called_once_with("bogdan")
    user_repository_mock.create.assert_called_once()


def test_register_rejects_existing_username():
    existing_user = SimpleNamespace(
        id=1,
        username="bogdan",
        password_hash="existing-hash",
    )

    user_repository_mock = Mock()
    user_repository_mock.get_by_username.return_value = existing_user

    auth_service = AuthService(user_repository_mock)

    with pytest.raises(ValueError, match="Username already exists"):
        auth_service.register("bogdan", "secret123")

    user_repository_mock.get_by_username.assert_called_once_with("bogdan")
    user_repository_mock.create.assert_not_called()


def test_login_returns_token_for_valid_credentials():
    password_hash = hash_password("secret123")

    existing_user = SimpleNamespace(
        id=1,
        username="bogdan",
        password_hash=password_hash,
    )

    user_repository_mock = Mock()
    user_repository_mock.get_by_username.return_value = existing_user

    auth_service = AuthService(user_repository_mock)

    access_token, user = auth_service.login("bogdan", "secret123")

    assert isinstance(access_token, str)
    assert access_token != ""
    assert user.username == "bogdan"

    user_repository_mock.get_by_username.assert_called_once_with("bogdan")


def test_login_rejects_invalid_password():
    password_hash = hash_password("secret123")

    existing_user = SimpleNamespace(
        id=1,
        username="bogdan",
        password_hash=password_hash,
    )

    user_repository_mock = Mock()
    user_repository_mock.get_by_username.return_value = existing_user

    auth_service = AuthService(user_repository_mock)

    with pytest.raises(ValueError, match="Invalid username or password"):
        auth_service.login("bogdan", "wrong-password")

    user_repository_mock.get_by_username.assert_called_once_with("bogdan")


def test_login_rejects_unknown_username():
    user_repository_mock = Mock()
    user_repository_mock.get_by_username.return_value = None

    auth_service = AuthService(user_repository_mock)

    with pytest.raises(ValueError, match="Invalid username or password"):
        auth_service.login("unknown-user", "secret123")