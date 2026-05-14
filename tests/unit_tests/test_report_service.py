from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

from app.service.report_service import ReportService


def make_session(session_id: int, end_time: datetime, ahi: float):
    return SimpleNamespace(
        id=session_id,
        end_time=end_time,
        ahi=ahi,
        has_smoked=False,
        has_drunk_alcohol=False,
    )


def test_generate_sleep_report_pdf_coordinates_dependencies():
    session_1 = make_session(1, datetime(2026, 5, 10), 10.0)
    session_2 = make_session(2, datetime(2026, 5, 11), 20.0)

    user = SimpleNamespace(
        id=1,
        username="bogdan",
        name="Bogdan",
    )

    session_repository_mock = Mock()
    pdf_report_service_mock = Mock()
    chart_service_mock = Mock()

    session_repository_mock.get_for_user_in_range.return_value = [
        session_2,
        session_1,
    ]

    chart_service_mock.build_overview_chart.return_value = b"overview-chart"
    chart_service_mock.select_sessions_for_detailed_charts.return_value = [
        session_1,
    ]
    chart_service_mock.build_session_chart.return_value = b"session-chart"
    chart_service_mock.chart_mode_label.return_value = "Detailed charts for the last 7 days"
    chart_service_mock.ahi_severity_label.return_value = "Mild"

    pdf_report_service_mock.build_sleep_report_pdf.return_value = b"%PDF-test"

    report_service = ReportService(
        session_repository_mock,
        pdf_report_service_mock,
        chart_service_mock,
    )

    result = report_service.generate_sleep_report_pdf(
        user=user,
        start_date=datetime(2026, 5, 1),
        end_date=datetime(2026, 5, 31),
        chart_mode="last_7_days",
    )

    assert result == b"%PDF-test"

    session_repository_mock.get_for_user_in_range.assert_called_once()
    chart_service_mock.build_overview_chart.assert_called_once()
    chart_service_mock.select_sessions_for_detailed_charts.assert_called_once()
    chart_service_mock.build_session_chart.assert_called_once_with(session_1)
    pdf_report_service_mock.build_sleep_report_pdf.assert_called_once()