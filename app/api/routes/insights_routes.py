from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dtos.insights_dto import WeeklyInsightsResponseDto
from app.config.database import get_db
from app.dependencies.auth_dependencies import get_current_user
from app.model.user import User
from app.repository.spo2_session_repository import Spo2SessionRepository
from app.service.insights_service import InsightsService

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/weekly", response_model=WeeklyInsightsResponseDto)
def get_weekly_insights(
    start_date: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = InsightsService(Spo2SessionRepository(db))

    return service.get_weekly_insights(
        user_id=current_user.id,
        start_date=start_date,
    )