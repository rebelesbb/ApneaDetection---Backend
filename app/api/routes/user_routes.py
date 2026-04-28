from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dtos.user_dto import (
    UserProfileResponseDto,
    UpdateUserProfileRequestDto,
)
from app.config.database import get_db
from app.dependencies.auth_dependencies import get_current_user
from app.model.user import User
from app.repository.user_repository import UserRepository
from app.service.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=UserProfileResponseDto)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=UserProfileResponseDto)
def update_my_profile(
    payload: UpdateUserProfileRequestDto,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_service = UserService(UserRepository(db))

    updated_user = user_service.update_profile(
        current_user,
        name=payload.name,
        height=payload.height,
        weight=payload.weight,
        age=payload.age,
        sleep_target=payload.sleep_target,
    )

    return updated_user