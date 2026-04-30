from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.models.user import User


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def get(self, user_id: int) -> User | None:
        return self.repo.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.repo.get_by_email(email)

    def create_user(self, email: str, hashed_password: str, role: str = "user") -> User:
        existing = self.repo.get_by_email(email)
        if existing:
            raise ValueError("User with this email already exists")

        return self.repo.create(email=email, hashed_password=hashed_password, role=role)
