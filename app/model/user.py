from typing import Optional
from sqlalchemy import String, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    height: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sleep_target: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    sessions = relationship("Spo2Session", back_populates="user", cascade="all, delete-orphan")