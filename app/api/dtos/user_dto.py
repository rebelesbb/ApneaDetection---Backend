from typing import Optional
from pydantic import BaseModel


class UserProfileResponseDto(BaseModel):
    id: int
    username: str
    name: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    age: Optional[int] = None
    sleep_target: Optional[int] = None

    class Config:
        from_attributes = True

class UpdateUserProfileRequestDto(BaseModel):
    name: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    age: Optional[int] = None
    sleep_target: Optional[int] = None