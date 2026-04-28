from datetime import datetime, timedelta

from app.repository.spo2_session_repository import Spo2SessionRepository


class InsightsService:
    def __init__(self, spo2_session_repository: Spo2SessionRepository):
        self.spo2_session_repository = spo2_session_repository

    def get_weekly_insights(self, *, user_id: int, start_date: datetime):
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)

        sessions = self.spo2_session_repository.get_for_user_in_range(
            user_id,
            date_from=start_date,
            date_to=end_date,
        )

        smoking_correlation = self._calculate_correlation_score(
            sessions=sessions,
            condition_fn=lambda s: s.has_smoked,
        )

        alcohol_correlation = self._calculate_correlation_score(
            sessions=sessions,
            condition_fn=lambda s: s.has_drunk_alcohol,
        )

        smoking_days_count = len([s for s in sessions if s.has_smoked])
        alcohol_days_count = len([s for s in sessions if s.has_drunk_alcohol])

        return {
            "start_date": start_date,
            "end_date": end_date,
            "sessions": sessions,
            "smoking_correlation": smoking_correlation,
            "alcohol_correlation": alcohol_correlation,
            "smoking_days_count": smoking_days_count,
            "alcohol_days_count": alcohol_days_count,
        }

    def _calculate_correlation_score(self, *, sessions, condition_fn):
        if not sessions:
            return 0.0

        with_condition = [s for s in sessions if condition_fn(s)]
        without_condition = [s for s in sessions if not condition_fn(s)]

        if not with_condition or not without_condition:
            return 0.0

        avg_with = sum(float(s.ahi) for s in with_condition) / len(with_condition)
        avg_without = sum(float(s.ahi) for s in without_condition) / len(without_condition)

        if avg_without == 0:
            return 0.0

        return ((avg_with - avg_without) / avg_without) * 100