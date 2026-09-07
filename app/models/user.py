# -*- coding: utf-8 -*-
"""
Модель користувача — ПРОФЕСІЙНА ФІНАЛЬНА ВЕРСІЯ
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import hashlib
import secrets

from app.db.base_class import Base


class UserRole:
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    USER = "user"

    @classmethod
    def choices(cls):
        return [cls.ADMIN, cls.MANAGER, cls.ANALYST, cls.USER]


class UserStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"

    @classmethod
    def choices(cls):
        return [cls.ACTIVE, cls.INACTIVE, cls.SUSPENDED, cls.BANNED]


class User(Base):
    __tablename__ = "users"

    # Ідентифікація
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    username = Column(String(100), nullable=True, index=True)

    # Аутентифікація
    hashed_password = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)

    # Профіль
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    phone_number = Column(String(20), nullable=True)
    bio = Column(Text, nullable=True)

    # Ролі та статуси
    role = Column(String(50), default=UserRole.USER, nullable=False)
    status = Column(String(20), default=UserStatus.ACTIVE, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Фінанси
    balance = Column(Float, default=0.0, nullable=False)
    total_spent = Column(Float, default=0.0, nullable=False)

    # Часові мітки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_active = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Налаштування
    preferences = Column(Text, nullable=True)

    # Зв’язки (усі мають ForeignKey у відповідних моделях)
    purchases = relationship("Purchase", back_populates="user", cascade="all, delete-orphan")
    balance_transactions = relationship("BalanceTransaction", back_populates="user", cascade="all, delete-orphan")
    intents_log = relationship("IntentsLog", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    requests = relationship("Request", back_populates="user", cascade="all, delete-orphan")

    # Властивості
    @property
    def display_name(self) -> str:
        return self.full_name or self.username or f"Telegram_{self.telegram_id}" if self.telegram_id else f"User_{self.id}"

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_active_user(self) -> bool:
        return self.is_active and self.status == UserStatus.ACTIVE

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    # Методи безпеки
    def set_password(self, raw_password: str) -> None:
        self.hashed_password = hashlib.sha256(raw_password.encode()).hexdigest()

    def check_password(self, raw_password: str) -> bool:
        return self.hashed_password == hashlib.sha256(raw_password.encode()).hexdigest()

    def generate_verification_token(self) -> str:
        token = secrets.token_hex(16)
        self.verification_token = token
        return token

    # Методи роботи з балансом
    def add_balance(self, amount: float) -> bool:
        if amount <= 0:
            return False
        self.balance += amount
        return True

    def deduct_balance(self, amount: float) -> bool:
        if amount <= 0 or self.balance < amount:
            return False
        self.balance -= amount
        self.total_spent += amount
        return True

    # Аналітика
    def purchase_count(self) -> int:
        return len(self.purchases)

    def average_purchase_amount(self) -> float:
        return sum(p.amount for p in self.purchases) / len(self.purchases) if self.purchases else 0.0

    def intents_count(self) -> int:
        return len(self.intents_log)

    # Конвертація
    def to_dict(self, include_sensitive: bool = False) -> dict:
        data = {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "display_name": self.display_name,
            "role": self.role,
            "status": self.status,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "is_verified": self.is_verified,
            "balance": self.balance,
            "total_spent": self.total_spent,
            "avatar_url": self.avatar_url,
            "phone_number": self.phone_number,
            "bio": self.bio,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "is_deleted": self.is_deleted,
            "purchase_count": self.purchase_count(),
            "average_purchase_amount": self.average_purchase_amount(),
            "intents_count": self.intents_count(),
        }
        if include_sensitive:
            data["hashed_password"] = self.hashed_password
            data["verification_token"] = self.verification_token
        return data

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, telegram_id={self.telegram_id}, role={self.role})>"

    def __str__(self) -> str:
        return self.display_name
