from types import SimpleNamespace
from unittest.mock import Mock

from app.service.user_service import UserService
from typing import cast
from app.model.user import User


def test_update_profile_delegates_to_repository():
    user = SimpleNamespace(
        id=1,
        username="bogdan",
        name=None,
        height=None,
        weight=None,
        age=None,
        sleep_target=None,
    )

    updated_user = SimpleNamespace(
        id=1,
        username="bogdan",
        name="Bogdan",
        height=180.0,
        weight=75.0,
        age=22,
        sleep_target=8,
    )

    user_repository_mock = Mock()
    user_repository_mock.update_profile.return_value = updated_user

    user_service = UserService(user_repository_mock)

    result = user_service.update_profile(
        cast(User, user),
        name="Bogdan",
        height=180.0,
        weight=75.0,
        age=22,
        sleep_target=8,
    )

    assert result.name == "Bogdan"
    assert result.height == 180.0
    assert result.weight == 75.0
    assert result.age == 22
    assert result.sleep_target == 8

    user_repository_mock.update_profile.assert_called_once_with(
        user,
        name="Bogdan",
        height=180.0,
        weight=75.0,
        age=22,
        sleep_target=8,
    )