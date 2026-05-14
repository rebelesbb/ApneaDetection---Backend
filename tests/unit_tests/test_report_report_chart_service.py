from datetime import datetime, timedelta
from types import SimpleNamespace

from app.service.report_chart_service import ReportChartService


def make_session(session_id: int, end_time: datetime, ahi: float = 10.0):
    return SimpleNamespace(
        id=session_id,
        end_time=end_time,
        ahi=ahi,
    )


def test_select_sessions_for_detailed_charts_returns_empty_for_none():
    service = ReportChartService()

    sessions = [
        make_session(1, datetime(2026, 5, 10)),
        make_session(2, datetime(2026, 5, 12)),
    ]

    selected = service.select_sessions_for_detailed_charts(
        sessions,
        "none",
    )

    assert selected == []


def test_select_sessions_for_detailed_charts_returns_all_sessions():
    service = ReportChartService()

    sessions = [
        make_session(1, datetime(2026, 5, 10)),
        make_session(2, datetime(2026, 5, 12)),
    ]

    selected = service.select_sessions_for_detailed_charts(
        sessions,
        "all",
    )

    assert selected == sessions


def test_select_sessions_for_detailed_charts_returns_last_3_days():
    service = ReportChartService()

    latest_end_time = datetime(2026, 5, 20)

    old_session = make_session(
        1,
        latest_end_time - timedelta(days=5),
    )
    recent_session = make_session(
        2,
        latest_end_time - timedelta(days=2),
    )
    latest_session = make_session(
        3,
        latest_end_time,
    )

    selected = service.select_sessions_for_detailed_charts(
        [old_session, recent_session, latest_session],
        "last_3_days",
    )

    assert selected == [recent_session, latest_session]


def test_ahi_severity_label_returns_expected_values():
    service = ReportChartService()

    assert service.ahi_severity_label(2.0) == "Normal"
    assert service.ahi_severity_label(10.0) == "Mild"
    assert service.ahi_severity_label(20.0) == "Moderate"
    assert service.ahi_severity_label(35.0) == "Severe"


def test_chart_mode_label_returns_readable_label():
    service = ReportChartService()

    assert service.chart_mode_label("none") == "No detailed session charts"
    assert service.chart_mode_label("last_3_days") == "Detailed charts for the last 3 days"
    assert service.chart_mode_label("last_7_days") == "Detailed charts for the last 7 days"
    assert service.chart_mode_label("all") == "Detailed charts for all sessions"