from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock
import pytest

from app.service.spo2_session_service import Spo2SessionService
from typing import cast
from app.model.user import User


def build_spo2_session_service():
    session_repository_mock = Mock()
    prediction_service_mock = Mock()

    spo2_session_service = Spo2SessionService(
        session_repository_mock,
        prediction_service_mock,
    )

    return spo2_session_service, session_repository_mock, prediction_service_mock


def test_analyze_and_create_session_saves_prediction_result():
    spo2_session_service, session_repository_mock, prediction_service_mock = (
        build_spo2_session_service()
    )

    spo2_values = [95.0] * 120
    timestamps = list(range(120))
    sleep_stages = [1] * 120
    predictions = [0] * 120
    predictions[10] = 1

    prediction_service_mock.predict.return_value = (12.5, predictions)
    session_repository_mock.create.side_effect = lambda session_data: session_data

    user = SimpleNamespace(id=1)

    created_session = spo2_session_service.analyze_and_create_session(
        user=cast(User, user),
        start_time=datetime(2026, 5, 12, 23, 0, 0),
        end_time=datetime(2026, 5, 13, 7, 0, 0),
        spo2values=spo2_values,
        timestamps=timestamps,
        sleep_stages=sleep_stages,
        has_smoked=False,
        has_drunk_alcohol=True,
    )

    assert created_session["user_id"] == 1
    assert created_session["spo2values"] == spo2_values
    assert created_session["timestamps"] == timestamps
    assert created_session["ahi"] == 12.5
    assert created_session["predictions"][10] == 1
    assert created_session["has_smoked"] is False
    assert created_session["has_drunk_alcohol"] is True

    prediction_service_mock.predict.assert_called_once_with(
        spo2_values,
        timestamps,
        sleep_stages,
    )
    session_repository_mock.create.assert_called_once()


def test_analyze_and_create_session_rejects_different_signal_and_timestamp_lengths():
    spo2_session_service, session_repository_mock, prediction_service_mock = (
        build_spo2_session_service()
    )

    user = SimpleNamespace(id=1)

    with pytest.raises(ValueError, match="Values and timestamps must have the same length"):
        spo2_session_service.analyze_and_create_session(
            user=cast(User, user),
            start_time=datetime(2026, 5, 12, 23, 0, 0),
            end_time=datetime(2026, 5, 13, 7, 0, 0),
            spo2values=[95.0] * 120,
            timestamps=list(range(119)),
            sleep_stages=[1] * 120,
            has_smoked=False,
            has_drunk_alcohol=False,
        )

    prediction_service_mock.predict.assert_not_called()
    session_repository_mock.create.assert_not_called()


def test_analyze_and_create_session_rejects_short_signal():
    spo2_session_service, session_repository_mock, prediction_service_mock = (
        build_spo2_session_service()
    )

    user = SimpleNamespace(id=1)

    with pytest.raises(ValueError, match="At least 60 samples are required"):
        spo2_session_service.analyze_and_create_session(
            user=cast(User, user),
            start_time=datetime(2026, 5, 12, 23, 0, 0),
            end_time=datetime(2026, 5, 13, 7, 0, 0),
            spo2values=[95.0] * 59,
            timestamps=list(range(59)),
            sleep_stages=[1] * 59,
            has_smoked=False,
            has_drunk_alcohol=False,
        )

    prediction_service_mock.predict.assert_not_called()
    session_repository_mock.create.assert_not_called()


def test_get_user_sessions_returns_all_sessions_when_no_date_range_is_given():
    spo2_session_service, session_repository_mock, _ = build_spo2_session_service()

    stored_session = SimpleNamespace(id=1, user_id=1)
    session_repository_mock.get_all_for_user.return_value = [stored_session]

    sessions = spo2_session_service.get_user_sessions(user_id=1)

    assert sessions == [stored_session]
    session_repository_mock.get_all_for_user.assert_called_once_with(1)
    session_repository_mock.get_for_user_in_range.assert_not_called()


def test_get_user_sessions_uses_date_range_when_provided():
    spo2_session_service, session_repository_mock, _ = build_spo2_session_service()

    date_from = datetime(2026, 5, 1)
    date_to = datetime(2026, 5, 31)
    stored_session = SimpleNamespace(id=1, user_id=1)

    session_repository_mock.get_for_user_in_range.return_value = [stored_session]

    sessions = spo2_session_service.get_user_sessions(
        user_id=1,
        date_from=date_from,
        date_to=date_to,
    )

    assert sessions == [stored_session]
    session_repository_mock.get_for_user_in_range.assert_called_once_with(
        1,
        date_from=date_from,
        date_to=date_to,
    )


def test_get_today_session_returns_current_user_session():
    spo2_session_service, session_repository_mock, _ = build_spo2_session_service()

    current_time = datetime(2026, 5, 13, 10, 0, 0)
    stored_session = SimpleNamespace(id=1, user_id=1)

    session_repository_mock.get_today_session_for_user.return_value = stored_session

    session = spo2_session_service.get_today_session(
        user_id=1,
        current_time=current_time,
    )

    assert session == stored_session
    session_repository_mock.get_today_session_for_user.assert_called_once_with(
        1,
        current_time,
    )


def test_update_session_flags_updates_existing_session():
    spo2_session_service, session_repository_mock, _ = build_spo2_session_service()

    stored_session = SimpleNamespace(
        id=1,
        user_id=1,
        has_smoked=False,
        has_drunk_alcohol=False,
    )

    updated_session = SimpleNamespace(
        id=1,
        user_id=1,
        has_smoked=True,
        has_drunk_alcohol=False,
    )

    session_repository_mock.get_by_id_for_user.return_value = stored_session
    session_repository_mock.update_flags.return_value = updated_session

    result = spo2_session_service.update_session_flags(
        user_id=1,
        session_id=1,
        has_smoked=True,
        has_drunk_alcohol=False,
    )

    assert result.has_smoked is True
    assert result.has_drunk_alcohol is False

    session_repository_mock.get_by_id_for_user.assert_called_once_with(1, 1)
    session_repository_mock.update_flags.assert_called_once_with(
        stored_session,
        has_smoked=True,
        has_drunk_alcohol=False,
    )


def test_update_session_flags_rejects_missing_session():
    spo2_session_service, session_repository_mock, _ = build_spo2_session_service()

    session_repository_mock.get_by_id_for_user.return_value = None

    with pytest.raises(ValueError, match="Session not found"):
        spo2_session_service.update_session_flags(
            user_id=1,
            session_id=999,
            has_smoked=True,
            has_drunk_alcohol=False,
        )

    session_repository_mock.update_flags.assert_not_called()