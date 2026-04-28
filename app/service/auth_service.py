from app.config.security import hash_password, verify_password, create_access_token
from app.repository.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register(self, username: str, password: str):
        existing_user = self.user_repository.get_by_username(username)
        if existing_user:
            raise ValueError("Username already exists")

        password_hash = hash_password(password)
        user = self.user_repository.create(username, password_hash)
        return user

    def login(self, username: str, password: str):
        user = self.user_repository.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid username or password")

        access_token = create_access_token(str(user.id))
        return access_token, user