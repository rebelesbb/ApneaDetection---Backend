from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dtos.report_dto import SleepReportRequestDto
from app.config.database import get_db
from app.dependencies.auth_dependencies import get_current_user
from app.model.user import User
from app.repository.spo2_session_repository import Spo2SessionRepository
from app.service.pdf_report_service import PdfReportService
from app.service.report_chart_service import ReportChartService
from app.service.report_service import ReportService
from pathlib import Path

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/sleep-pdf")
def generate_sleep_pdf_report(
    payload: SleepReportRequestDto,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        report_service = ReportService(
            Spo2SessionRepository(db),
            PdfReportService(),
            ReportChartService(),
        )

        pdf_bytes = report_service.generate_sleep_report_pdf(
            user=current_user,
            start_date=payload.start_date,
            end_date=payload.end_date,
            chart_mode=payload.chart_mode,
        )

        debug_dir = Path("debug_reports")
        debug_dir.mkdir(exist_ok=True)

        debug_file = debug_dir / "last_sleep_report.pdf"
        debug_file.write_bytes(pdf_bytes)
        print(f"PDF saved locally at: {debug_file.resolve()}")

        filename = (
            f"sleep_report_{payload.start_date.strftime('%Y%m%d')}_"
            f"{payload.end_date.strftime('%Y%m%d')}.pdf"
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF report: {str(e)}",
        )