from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.model.spo2_session import Spo2Session


class Spo2SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, session_data: dict) -> Spo2Session:
        session = Spo2Session(**session_data)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_all_for_user(self, user_id: int) -> list[Spo2Session]:
        return (
            self.db.query(Spo2Session)
            .filter(Spo2Session.user_id == user_id)
            .order_by(Spo2Session.start_time.desc())
            .all()
        )

    def get_for_user_in_range(
        self,
        user_id: int,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[Spo2Session]:
        query = self.db.query(Spo2Session).filter(Spo2Session.user_id == user_id)

        if date_from is not None:
            query = query.filter(Spo2Session.end_time >= date_from)

        if date_to is not None:
            query = query.filter(Spo2Session.end_time <= date_to)

        return query.order_by(Spo2Session.end_time.desc()).all()

    def get_today_session_for_user(
        self,
        user_id: int,
        current_time: datetime,
    ) -> Spo2Session | None:
        today_start = datetime(current_time.year, current_time.month, current_time.day)
        tomorrow_start = today_start + timedelta(days=1)
        yesterday_start = today_start - timedelta(days=1)

        sessions = (
            self.db.query(Spo2Session)
            .filter(
                Spo2Session.user_id == user_id,
                Spo2Session.end_time >= today_start,
                Spo2Session.end_time < tomorrow_start,
                Spo2Session.start_time >= yesterday_start,
            )
            .order_by(Spo2Session.start_time.desc())
            .all()
        )

        return sessions[0] if sessions else None

    def get_by_id_for_user(self, session_id: int, user_id: int) -> Spo2Session | None:
        return (
            self.db.query(Spo2Session)
            .filter(
                Spo2Session.id == session_id,
                Spo2Session.user_id == user_id,
            )
            .first()
        )

    def update_flags(
        self,
        session: Spo2Session,
        *,
        has_smoked: bool,
        has_drunk_alcohol: bool,
    ) -> Spo2Session:
        session.has_smoked = has_smoked
        session.has_drunk_alcohol = has_drunk_alcohol

        self.db.commit()
        self.db.refresh(session)
        return session