import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jwt
from dotenv import load_dotenv
from passlib.context import CryptContext


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
)

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not configured. Please define it in the .env file.")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])