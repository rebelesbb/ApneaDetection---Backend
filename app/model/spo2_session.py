from datetime import datetime
from sqlalchemy import Integer, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base


class Spo2Session(Base):
    __tablename__ = "spo2_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    spo2values: Mapped[list] = mapped_column(JSONB, nullable=False)
    timestamps: Mapped[list] = mapped_column(JSONB, nullable=False)
    predictions: Mapped[list] = mapped_column(JSONB, nullable=False)

    ahi: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)

    has_smoked: Mapped[bool] = mapped_column(Boolean, default=False)
    has_drunk_alcohol: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User", back_populates="sessions")