import io
from datetime import timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D


class ReportChartService:
    def build_overview_chart(self, sessions: list):
        fig, ax = plt.subplots(figsize=(10, 4.5))

        if not sessions:
            ax.text(0.5, 0.5, "No data available", ha="center", va="center", fontsize=14)
            ax.axis("off")
        else:
            labels = [s.end_time.strftime("%d %b") for s in sessions]
            values = [float(s.ahi) for s in sessions]
            colors = [self._ahi_color(v) for v in values]

            ax.bar(labels, values, color=colors)

            ax.axhline(5, linestyle="--", linewidth=1, alpha=0.8)
            ax.axhline(15, linestyle="--", linewidth=1, alpha=0.8)
            ax.axhline(30, linestyle="--", linewidth=1, alpha=0.8)

            ax.set_title("AHI Overview by Session Date", fontsize=13, fontweight="bold")
            ax.set_ylabel("AHI")
            ax.set_xlabel("Session date")
            ax.tick_params(axis="x", rotation=35)

            legend_elements = [
                Patch(facecolor=self._ahi_color(2), label="Normal (<5)"),
                Patch(facecolor=self._ahi_color(10), label="Mild (5–15)"),
                Patch(facecolor=self._ahi_color(20), label="Moderate (15–30)"),
                Patch(facecolor=self._ahi_color(35), label="Severe (30+)"),
            ]
            ax.legend(handles=legend_elements, loc="upper right", fontsize=9)

        fig.tight_layout()
        return self._fig_to_bytes(fig)

    def build_session_chart(self, session):
        fig, ax = plt.subplots(figsize=(10, 4.2))

        x = list(session.timestamps)
        y = [float(v) for v in session.values]

        for idx, pred in enumerate(session.predictions):
            if int(pred) == 1:
                start_sec = idx * 60
                end_sec = start_sec + 60
                ax.axvspan(start_sec, end_sec, alpha=0.20, color="red")

        ax.plot(x, y, linewidth=1.2)

        duration_minutes = int((session.end_time - session.start_time).total_seconds() // 60)

        ax.set_title(
            f"SpO2 Session - {session.end_time.strftime('%d %b %Y')} | "
            f"AHI: {float(session.ahi):.2f} | Duration: {duration_minutes} min",
            fontsize=12,
            fontweight="bold",
        )
        ax.set_xlabel("Seconds")
        ax.set_ylabel("SpO2")
        ax.set_ylim(bottom=min(min(y) - 1, 80), top=max(max(y) + 1, 100))

        legend_elements = [
            Line2D([0], [0], color="blue", lw=1.5, label="SpO2 signal"),
            Patch(facecolor="red", alpha=0.20, label="Detected apnea-related window"),
        ]
        ax.legend(handles=legend_elements, loc="lower left", fontsize=9)

        fig.tight_layout()
        return self._fig_to_bytes(fig)

    def select_sessions_for_detailed_charts(self, sessions: list, chart_mode: str) -> list:
        if chart_mode == "none":
            return []

        if chart_mode == "all":
            return sessions

        if not sessions:
            return []

        latest_end_time = max(s.end_time for s in sessions)

        if chart_mode == "last_3_days":
            threshold = latest_end_time - timedelta(days=3)
        elif chart_mode == "last_7_days":
            threshold = latest_end_time - timedelta(days=7)
        else:
            return []

        return [s for s in sessions if s.end_time >= threshold]

    def chart_mode_label(self, chart_mode: str) -> str:
        mapping = {
            "none": "No detailed session charts",
            "last_3_days": "Detailed charts for the last 3 days",
            "last_7_days": "Detailed charts for the last 7 days",
            "all": "Detailed charts for all sessions",
        }
        return mapping.get(chart_mode, chart_mode)

    def ahi_severity_label(self, ahi: float) -> str:
        if ahi < 5:
            return "Normal"
        if ahi < 15:
            return "Mild"
        if ahi < 30:
            return "Moderate"
        return "Severe"

    def _ahi_color(self, ahi: float):
        if ahi < 5:
            return "#37c978"  
        if ahi < 15:
            return "#f0c14b"  
        if ahi < 30:
            return "#f28c28"  
        return "#d9534f"      

    def _fig_to_bytes(self, fig):
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        buffer.seek(0)
        return buffer