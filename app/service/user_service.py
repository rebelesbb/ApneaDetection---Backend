from app.model.user import User
from app.repository.user_repository import UserRepository

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def update_profile(
        self,
        user: User,
        *,
        name: str | None,
        height: float | None,
        weight: float | None,
        age: int | None,
        sleep_target: int | None,
    ) -> User:
        return self.user_repository.update_profile(
            user,
            name=name,
            height=height,
            weight=weight,
            age=age,
            sleep_target=sleep_target,
        )