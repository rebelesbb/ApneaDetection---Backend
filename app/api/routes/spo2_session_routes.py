from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dtos.spo2_session_dto import (
    AnalyzeSpo2SessionRequestDto,
    Spo2SessionResponseDto,
    UpdateSpo2SessionRequestDto,
)
from app.config.database import get_db
from app.dependencies.auth_dependencies import get_current_user
from app.model.user import User
from app.repository.spo2_session_repository import Spo2SessionRepository
from app.service.apnea_prediction_service import ApneaPredictionService
from app.service.spo2_session_service import Spo2SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])

apnea_prediction_service = ApneaPredictionService()


@router.post("/analyze", response_model=Spo2SessionResponseDto, status_code=status.HTTP_201_CREATED)
def analyze_session(
    payload: AnalyzeSpo2SessionRequestDto,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = Spo2SessionService(
        Spo2SessionRepository(db),
        apnea_prediction_service,
    )

    try:
        return service.analyze_and_create_session(
            user=current_user,
            start_time=payload.start_time,
            end_time=payload.end_time,
            spo2values=payload.spo2values,
            timestamps=payload.timestamps,
            sleep_stages=payload.sleep_stages,
            has_smoked=payload.has_smoked,
            has_drunk_alcohol=payload.has_drunk_alcohol,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=list[Spo2SessionResponseDto])
def get_sessions(
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = Spo2SessionService(
        Spo2SessionRepository(db),
        apnea_prediction_service,
    )

    return service.get_user_sessions(
        user_id=current_user.id,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/today", response_model=Spo2SessionResponseDto | None)
def get_today_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = Spo2SessionService(
        Spo2SessionRepository(db),
        apnea_prediction_service,
    )

    return service.get_today_session(
        user_id=current_user.id,
        current_time=datetime.now(),
    )


@router.put("/{session_id}", response_model=Spo2SessionResponseDto)
def update_session(
    session_id: int,
    payload: UpdateSpo2SessionRequestDto,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = Spo2SessionService(
        Spo2SessionRepository(db),
        apnea_prediction_service,
    )

    try:
        return service.update_session_flags(
            user_id=current_user.id,
            session_id=session_id,
            has_smoked=payload.has_smoked,
            has_drunk_alcohol=payload.has_drunk_alcohol,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))