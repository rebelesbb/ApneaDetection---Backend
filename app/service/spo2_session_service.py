from datetime import datetime

from app.model.user import User
from app.repository.spo2_session_repository import Spo2SessionRepository
from app.service.apnea_prediction_service import ApneaPredictionService


class Spo2SessionService:
    def __init__(
        self,
        spo2_session_repository: Spo2SessionRepository,
        apnea_prediction_service: ApneaPredictionService,
    ):
        self.spo2_session_repository = spo2_session_repository
        self.apnea_prediction_service = apnea_prediction_service

    def analyze_and_create_session(
        self,
        *,
        user: User,
        start_time: datetime,
        end_time: datetime,
        spo2values: list[float],
        timestamps: list[int],
        sleep_stages: list[int],
        has_smoked: bool,
        has_drunk_alcohol: bool,
    ):
        if len(spo2values) != len(timestamps):
            raise ValueError("Values and timestamps must have the same length.")

        if len(spo2values) < 60:
            raise ValueError("At least 60 samples are required.")

        ahi, predictions = self.apnea_prediction_service.predict(spo2values, timestamps, sleep_stages)

        return self.spo2_session_repository.create({
            "user_id": user.id,
            "start_time": start_time,
            "end_time": end_time,
            "spo2values": spo2values,
            "timestamps": timestamps,
            "predictions": predictions,
            "ahi": ahi,
            "has_smoked": has_smoked,
            "has_drunk_alcohol": has_drunk_alcohol,
        })

    def get_user_sessions(
        self,
        *,
        user_id: int,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ):
        if date_from is None and date_to is None:
            return self.spo2_session_repository.get_all_for_user(user_id)

        return self.spo2_session_repository.get_for_user_in_range(
            user_id,
            date_from=date_from,
            date_to=date_to,
        )

    def get_today_session(self, *, user_id: int, current_time: datetime):
        return self.spo2_session_repository.get_today_session_for_user(user_id, current_time)

    def update_session_flags(
        self,
        *,
        user_id: int,
        session_id: int,
        has_smoked: bool,
        has_drunk_alcohol: bool,
    ):
        session = self.spo2_session_repository.get_by_id_for_user(session_id, user_id)
        if session is None:
            raise ValueError("Session not found")

        return self.spo2_session_repository.update_flags(
            session,
            has_smoked=has_smoked,
            has_drunk_alcohol=has_drunk_alcohol,
        )