from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)

    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    user = relationship("User", back_populates="purchases")
    agent = relationship("Agent", back_populates="purchases")


# 🔥 ВАЖЛИВО: імпортуємо залежні моделі ПІСЛЯ визначення Purchase
from app.models.agent import Agent
from app.models.user import User
