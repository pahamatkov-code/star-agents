from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.security import hash_password


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def get(self, user_id: int) -> Optional[User]:
        """Отримати користувача за ID."""
        return self.repo.get(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        """Отримати користувача за email."""
        return self.repo.get_by_email(email)

    def create_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        username: Optional[str] = None,
        telegram_id: Optional[str] = None,
        phone_number: Optional[str] = None,
        avatar_url: Optional[str] = None,
        bio: Optional[str] = None,
        role: str = "user",
        status: str = "active",
        is_active: bool = True,
        is_superuser: bool = False,
        balance: float = 0.0,
        preferences: Optional[dict] = None,
    ) -> User:
        """
        Створити нового користувача з максимальною кількістю полів.
        Виконує перевірку на дублювання email.
        """

        existing = self.repo.get_by_email(email)
        if existing:
            raise ValueError("User with this email already exists")

        user = self.repo.create(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            username=username,
            telegram_id=telegram_id,
            phone_number=phone_number,
            avatar_url=avatar_url,
            bio=bio,
            role=role,
            status=status,
            is_active=is_active,
            is_superuser=is_superuser,
            balance=balance,
            preferences=preferences,
        )
        return user
