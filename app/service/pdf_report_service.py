import io
from statistics import mean
from datetime import timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


class PdfReportService:
    def build_sleep_report_pdf(
        self,
        *,
        user,
        start_date,
        end_date,
        sessions: list,
        chart_mode_label: str,
        overview_chart_buffer,
        detailed_chart_buffers: list[tuple],
        chart_legend_note: str,
        average_severity_label: str | None,
    ) -> bytes:
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)

        width, height = A4
        margin_x = 1.6 * cm
        usable_width = width - 2 * margin_x
        y = height - 1.4 * cm

        def new_page():
            nonlocal y
            pdf.showPage()
            y = height - 1.4 * cm

        def ensure_space(required_height: float):
            nonlocal y
            if y - required_height < 1.5 * cm:
                new_page()

        def line_break(amount: float):
            nonlocal y
            y -= amount

        def draw_text(text: str, x: float, size: int = 11, bold: bool = False, color=colors.black):
            font_name = "Helvetica-Bold" if bold else "Helvetica"
            pdf.setFont(font_name, size)
            pdf.setFillColor(color)
            pdf.drawString(x, y, text)

        def draw_wrapped_lines(lines: list[str], x: float, size: int = 10, leading: float = 13):
            nonlocal y
            pdf.setFillColor(colors.black)
            pdf.setFont("Helvetica", size)
            for line in lines:
                pdf.drawString(x, y, line)
                y -= leading

        def draw_section_title(title: str):
            nonlocal y
            pdf.setFillColor(colors.HexColor("#1f2d3d"))
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(margin_x, y, title)
            y -= 8
            pdf.setStrokeColor(colors.HexColor("#c7d0d9"))
            pdf.line(margin_x, y, margin_x + usable_width, y)
            y -= 14

        def draw_info_box(title: str, lines: list[str], box_height: float):
            nonlocal y
            ensure_space(box_height + 10)
            box_y = y - box_height

            pdf.setFillColor(colors.HexColor("#f5f7fa"))
            pdf.setStrokeColor(colors.HexColor("#d6dde5"))
            pdf.roundRect(margin_x, box_y, usable_width, box_height, 10, fill=1, stroke=1)

            y -= 18
            pdf.setFillColor(colors.HexColor("#1f2d3d"))
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(margin_x + 12, y, title)
            y -= 16

            pdf.setFillColor(colors.black)
            pdf.setFont("Helvetica", 10)
            for line in lines:
                pdf.drawString(margin_x + 12, y, line)
                y -= 13

            y = box_y - 12

        def format_duration(start_time, end_time):
            total_minutes = int((end_time - start_time).total_seconds() // 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}m"

        pdf.setFillColor(colors.HexColor("#1f2d3d"))
        pdf.setFont("Helvetica-Bold", 22)
        pdf.drawString(margin_x, y, "Sleep Monitoring Report")
        line_break(24)

        pdf.setStrokeColor(colors.HexColor("#aab7c4"))
        pdf.line(margin_x, y, margin_x + usable_width, y)
        line_break(16)

        draw_text(
            f"Reporting period: {start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}",
            margin_x,
            size=11,
        )
        line_break(14)
        draw_text(f"Generated on: {end_date.now().strftime('%d %b %Y %H:%M') if hasattr(end_date, 'now') else ''}", margin_x, size=11)
        line_break(14)
        draw_text(f"Detailed charts included: {chart_mode_label}", margin_x, size=11)
        line_break(18)

        profile_lines = []

        if getattr(user, "username", None):
            profile_lines.append(f"Username: {user.username}")
        if getattr(user, "name", None):
            profile_lines.append(f"Name: {user.name}")
        if getattr(user, "age", None) is not None:
            profile_lines.append(f"Age: {user.age}")
        if getattr(user, "height", None) is not None:
            profile_lines.append(f"Height: {float(user.height):.1f} cm")
        if getattr(user, "weight", None) is not None:
            profile_lines.append(f"Weight: {float(user.weight):.1f} kg")

        if profile_lines:
            draw_info_box("Patient Profile", profile_lines, box_height=max(48, 16 + len(profile_lines) * 13 + 16))
            line_break(14)

        draw_section_title("Summary")

        if sessions:
            ahi_values = [float(s.ahi) for s in sessions]
            smoking_count = len([s for s in sessions if s.has_smoked])
            alcohol_count = len([s for s in sessions if s.has_drunk_alcohol])

            summary_lines = [
                f"Sleep sessions analyzed: {len(sessions)}",
                f"Average AHI: {mean(ahi_values):.2f}",
                f"Minimum AHI: {min(ahi_values):.2f}",
                f"Maximum AHI: {max(ahi_values):.2f}",
                f"Average severity: {average_severity_label or 'N/A'}",
                f"Sessions marked with smoking: {smoking_count}",
                f"Sessions marked with alcohol: {alcohol_count}",
            ]
        else:
            summary_lines = ["No sessions found for the selected interval."]

        draw_info_box("Session Summary", summary_lines, box_height=max(60, 16 + len(summary_lines) * 13 + 16))

        line_break(18)
        draw_section_title("Overview Chart")
        ensure_space(9.2 * cm)

        pdf.drawImage(
            ImageReader(overview_chart_buffer),
            margin_x,
            y - 7.8 * cm,
            width=17 * cm,
            height=7.8 * cm,
            preserveAspectRatio=True,
            mask="auto",
        )
        line_break(8.1 * cm)

        new_page()
        draw_section_title("Detailed Session Review")
        line_break(16)

        chart_map = {session_id: chart_buffer for session_id, chart_buffer in detailed_chart_buffers}

        if not sessions:
            draw_text("No detailed session data available.", margin_x, size=10)
            line_break(14)
        else:
            for session in sessions:
                ensure_space(10 * cm)

                night_date = session.end_time - timedelta(days=1)

                pdf.setFillColor(colors.HexColor("#1f2d3d"))
                pdf.setFont("Helvetica-Bold", 13)
                pdf.drawString(
                    margin_x,
                    y,
                    f"Sleep Session {night_date.strftime('%d')} - {session.end_time.strftime('%d %b %Y')}",
                )
                line_break(14)

                details_lines = [
                    f"Start time: {session.start_time.strftime('%d %b %Y %H:%M')}",
                    f"End time: {session.end_time.strftime('%d %b %Y %H:%M')}",
                    f"Duration: {format_duration(session.start_time, session.end_time)}",
                    f"AHI: {float(session.ahi):.2f}",
                    f"Severity: {self._severity_label(float(session.ahi))}",
                    f"Smoking marker: {'Yes' if session.has_smoked else 'No'}",
                    f"Alcohol marker: {'Yes' if session.has_drunk_alcohol else 'No'}",
                ]

                draw_info_box(
                    "Details",
                    details_lines,
                    box_height=max(70, 16 + len(details_lines) * 13 + 16),
                )

                chart_buffer = chart_map.get(session.id)
                if chart_buffer is not None:
                    line_break(14)
                    draw_text("Sleep Chart", margin_x, size=12, bold=True, color=colors.HexColor("#1f2d3d"))
                    line_break(14)

                    ensure_space(6.8 * cm)
                    pdf.drawImage(
                        ImageReader(chart_buffer),
                        margin_x,
                        y - 5.8 * cm,
                        width=17 * cm,
                        height=5.8 * cm,
                        preserveAspectRatio=True,
                        mask="auto",
                    )
                    line_break(6.1 * cm)

                    pdf.setFillColor(colors.HexColor("#555555"))
                    pdf.setFont("Helvetica-Oblique", 9)
                    pdf.drawString(margin_x, y, chart_legend_note)
                    line_break(18)

                pdf.setStrokeColor(colors.HexColor("#dde3ea"))
                pdf.line(margin_x, y, margin_x + usable_width, y)
                line_break(18)

        ensure_space(3 * cm)
        draw_section_title("Notes")
        disclaimer_lines = [
            "This report is generated automatically based on SpO2 data and model predictions.",
            "It is intended for informational purposes and does not replace medical diagnosis.",
        ]
        draw_wrapped_lines(disclaimer_lines, margin_x, size=10, leading=13)

        pdf.save()
        buffer.seek(0)
        return buffer.getvalue()

    def _severity_label(self, ahi: float) -> str:
        if ahi < 5:
            return "Normal"
        if ahi < 15:
            return "Mild"
        if ahi < 30:
            return "Moderate"
        return "Severe"