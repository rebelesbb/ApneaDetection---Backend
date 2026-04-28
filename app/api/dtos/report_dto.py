from datetime import datetime
from typing import Literal

from pydantic import BaseModel, model_validator


ChartMode = Literal["none", "last_3_days", "last_7_days", "all"]


class SleepReportRequestDto(BaseModel):
    start_date: datetime
    end_date: datetime
    chart_mode: ChartMode

    @model_validator(mode="after")
    def validate_range(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")

        if (self.end_date - self.start_date).days > 31:
            raise ValueError("The export interval cannot exceed 31 days")

        return self