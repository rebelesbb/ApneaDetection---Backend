from datetime import datetime
from typing import Any, cast
import pytest
from pydantic import ValidationError

from app.api.dtos.report_dto import SleepReportRequestDto


def test_sleep_report_request_accepts_valid_interval():
    request = SleepReportRequestDto(
        start_date=datetime(2026, 5, 1),
        end_date=datetime(2026, 5, 10),
        chart_mode="last_7_days",
    )

    assert request.chart_mode == "last_7_days"


def test_sleep_report_request_rejects_end_date_before_start_date():
    with pytest.raises(ValidationError):
        SleepReportRequestDto(
            start_date=datetime(2026, 5, 10),
            end_date=datetime(2026, 5, 1),
            chart_mode="last_7_days",
        )


def test_sleep_report_request_rejects_interval_longer_than_31_days():
    with pytest.raises(ValidationError):
        SleepReportRequestDto(
            start_date=datetime(2026, 5, 1),
            end_date=datetime(2026, 6, 10),
            chart_mode="last_7_days",
        )


def test_sleep_report_request_rejects_invalid_chart_mode():
    with pytest.raises(ValidationError):
        SleepReportRequestDto(
            start_date=datetime(2026, 5, 1),
            end_date=datetime(2026, 5, 10),
            chart_mode=cast(Any, "invalid"),
        )