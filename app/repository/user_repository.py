from sqlalchemy.orm import Session
from app.model.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def create(self, username: str, password_hash: str) -> User:
        user = User(
            username=username,
            password_hash=password_hash
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
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
        user.name = name
        user.height = height
        user.weight = weight
        user.age = age
        user.sleep_target = sleep_target

        self.db.commit()
        self.db.refresh(user)
        return user