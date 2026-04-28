from datetime import datetime
from pydantic import BaseModel, Field


class AnalyzeSpo2SessionRequestDto(BaseModel):
    start_time: datetime
    end_time: datetime
    values: list[float] = Field(min_length=60)
    timestamps: list[int] = Field(min_length=60)
    has_smoked: bool = False
    has_drunk_alcohol: bool = False

class UpdateSpo2SessionRequestDto(BaseModel):
    has_smoked: bool
    has_drunk_alcohol: bool

class Spo2SessionResponseDto(BaseModel):
    id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    values: list[float]
    timestamps: list[int]
    predictions: list[int]
    ahi: float
    has_smoked: bool
    has_drunk_alcohol: bool

    class Config:
        from_attributes = True