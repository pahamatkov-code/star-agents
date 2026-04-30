from sqlalchemy.orm import Session
from app.models import User
from app.schemas.user import UserCreate
from app.core.security import hash_password


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: UserCreate) -> User:
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            is_active=data.is_active,
            role=data.role
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()
