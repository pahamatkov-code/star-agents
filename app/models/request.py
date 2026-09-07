# -*- coding: utf-8 -*-
"""
Модель запиту — ПРОФЕСІЙНА ФІНАЛЬНА ВЕРСІЯ
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Request(Base):
    __tablename__ = "requests"

    # Ідентифікація
    id = Column(Integer, primary_key=True, index=True)

    # ForeignKey на користувача
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Основні дані запиту
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=True)
    response_time = Column(Float, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Часова мітка
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Відношення до User
    user = relationship("User", back_populates="requests")

    def __repr__(self):
        return f"<Request(id={self.id}, endpoint={self.endpoint}, user_id={self.user_id})>"
