from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

from app.service.insights_service import InsightsService


def test_weekly_insights_calculates_counts_and_correlations():
    sessions = [
        SimpleNamespace(ahi=20.0, has_smoked=True, has_drunk_alcohol=False),
        SimpleNamespace(ahi=10.0, has_smoked=False, has_drunk_alcohol=False),
        SimpleNamespace(ahi=30.0, has_smoked=True, has_drunk_alcohol=True),
        SimpleNamespace(ahi=10.0, has_smoked=False, has_drunk_alcohol=False),
    ]

    session_repository_mock = Mock()
    session_repository_mock.get_for_user_in_range.return_value = sessions

    insights_service = InsightsService(session_repository_mock)

    result = insights_service.get_weekly_insights(
        user_id=1,
        start_date=datetime(2026, 5, 11),
    )

    assert result["sessions"] == sessions
    assert result["smoking_days_count"] == 2
    assert result["alcohol_days_count"] == 1
    assert result["smoking_correlation"] == 150.0
    assert round(result["alcohol_correlation"], 2) == 125.0

    session_repository_mock.get_for_user_in_range.assert_called_once()


def test_weekly_insights_returns_zero_correlations_when_no_sessions_exist():
    session_repository_mock = Mock()
    session_repository_mock.get_for_user_in_range.return_value = []

    insights_service = InsightsService(session_repository_mock)

    result = insights_service.get_weekly_insights(
        user_id=1,
        start_date=datetime(2026, 5, 11),
    )

    assert result["sessions"] == []
    assert result["smoking_correlation"] == 0.0
    assert result["alcohol_correlation"] == 0.0
    assert result["smoking_days_count"] == 0
    assert result["alcohol_days_count"] == 0


def test_weekly_insights_returns_zero_correlation_when_only_one_group_exists():
    sessions = [
        SimpleNamespace(ahi=20.0, has_smoked=True, has_drunk_alcohol=False),
        SimpleNamespace(ahi=25.0, has_smoked=True, has_drunk_alcohol=False),
    ]

    session_repository_mock = Mock()
    session_repository_mock.get_for_user_in_range.return_value = sessions

    insights_service = InsightsService(session_repository_mock)

    result = insights_service.get_weekly_insights(
        user_id=1,
        start_date=datetime(2026, 5, 11),
    )

    assert result["smoking_correlation"] == 0.0