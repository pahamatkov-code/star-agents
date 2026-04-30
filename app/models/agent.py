from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=True)
    email = Column(String, nullable=True)
    department = Column(String, nullable=True)
    skills = Column(String, nullable=True)
    status = Column(Boolean, default=True)
    price = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ❗ ВАЖЛИВО: НІЯКОГО user_id тут НЕМАЄ
    # Зв’язок з User відбувається через Purchase

    purchases = relationship("Purchase", back_populates="agent")
