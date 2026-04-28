from pydantic import BaseModel, Field

class RegisterRequestDto(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=6)


class LoginRequestDto(BaseModel):
    username: str
    password: str


class UserResponseDto(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class AuthResponseDto(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponseDto