from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dtos.auth_dto import (
    RegisterRequestDto,
    LoginRequestDto,
    UserResponseDto,
    AuthResponseDto,
)
from app.api.dtos.user_dto import UserProfileResponseDto
from app.config.database import get_db
from app.dependencies.auth_dependencies import get_current_user
from app.repository.user_repository import UserRepository
from app.service.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponseDto, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequestDto, db: Session = Depends(get_db)):
    auth_service = AuthService(UserRepository(db))

    try:
        print("Registering user:", payload.username)
        print("Password:", payload.password)
        user = auth_service.register(payload.username, payload.password)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponseDto)
def login(payload: LoginRequestDto, db: Session = Depends(get_db)):
    auth_service = AuthService(UserRepository(db))

    try:
        access_token, user = auth_service.login(payload.username, payload.password)
        return AuthResponseDto(
            access_token=access_token,
            user=user
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/profile", response_model=UserProfileResponseDto)
def get_me(current_user = Depends(get_current_user)):
    return current_user