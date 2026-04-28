from datetime import datetime
from pydantic import BaseModel

from app.api.dtos.spo2_session_dto import Spo2SessionResponseDto


class WeeklyInsightsResponseDto(BaseModel):
    start_date: datetime
    end_date: datetime
    sessions: list[Spo2SessionResponseDto]
    smoking_correlation: float
    alcohol_correlation: float
    smoking_days_count: int
    alcohol_days_count: int