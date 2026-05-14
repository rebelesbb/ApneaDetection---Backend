from datetime import datetime
from types import SimpleNamespace

import io
import matplotlib.pyplot as plt

from app.service.pdf_report_service import PdfReportService


def make_empty_chart_buffer():
    buffer = io.BytesIO()

    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, "Test chart", ha="center")
    fig.savefig(buffer, format="png")
    plt.close(fig)

    buffer.seek(0)
    return buffer


def test_pdf_report_service_generates_pdf_bytes_without_sessions():
    service = PdfReportService()

    user = SimpleNamespace(
        username="bogdan",
        name="Bogdan",
        age=22,
        height=180.0,
        weight=75.0,
    )

    pdf_bytes = service.build_sleep_report_pdf(
        user=user,
        start_date=datetime(2026, 5, 1),
        end_date=datetime(2026, 5, 10),
        sessions=[],
        chart_mode_label="No detailed session charts",
        overview_chart_buffer=make_empty_chart_buffer(),
        detailed_chart_buffers=[],
        chart_legend_note="Test legend",
        average_severity_label=None,
    )

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000