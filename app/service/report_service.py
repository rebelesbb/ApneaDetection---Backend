from statistics import mean

from app.repository.spo2_session_repository import Spo2SessionRepository
from app.service.pdf_report_service import PdfReportService
from app.service.report_chart_service import ReportChartService


class ReportService:
    def __init__(
        self,
        spo2_session_repository: Spo2SessionRepository,
        pdf_report_service: PdfReportService,
        report_chart_service: ReportChartService,
    ):
        self.spo2_session_repository = spo2_session_repository
        self.pdf_report_service = pdf_report_service
        self.report_chart_service = report_chart_service

    def generate_sleep_report_pdf(
        self,
        *,
        user,
        start_date,
        end_date,
        chart_mode: str,
    ) -> bytes:
        sessions = self.spo2_session_repository.get_for_user_in_range(
            user.id,
            date_from=start_date,
            date_to=end_date,
        )

        sessions = sorted(sessions, key=lambda s: s.end_time)

        overview_chart_buffer = self.report_chart_service.build_overview_chart(sessions)

        detailed_sessions = self.report_chart_service.select_sessions_for_detailed_charts(
            sessions,
            chart_mode,
        )

        detailed_chart_buffers = [
            (session.id, self.report_chart_service.build_session_chart(session))
            for session in detailed_sessions
        ]

        chart_mode_label = self.report_chart_service.chart_mode_label(chart_mode)

        average_severity_label = None
        if sessions:
            average_ahi = mean(float(s.ahi) for s in sessions)
            average_severity_label = self.report_chart_service.ahi_severity_label(average_ahi)

        chart_legend_note = (
            "Blue line = SpO2 signal. Red shaded areas = windows classified by the model "
            "as apnea-related events."
        )

        return self.pdf_report_service.build_sleep_report_pdf(
            user=user,
            start_date=start_date,
            end_date=end_date,
            sessions=sessions,
            chart_mode_label=chart_mode_label,
            overview_chart_buffer=overview_chart_buffer,
            detailed_chart_buffers=detailed_chart_buffers,
            chart_legend_note=chart_legend_note,
            average_severity_label=average_severity_label,
        )