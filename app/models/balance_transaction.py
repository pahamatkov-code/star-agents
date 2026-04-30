from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class BalanceTransaction(Base):
    __tablename__ = "balance_transactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Integer, nullable=False)
    type = Column(String(20), nullable=False)  # "topup" | "spend"

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="balance_transactions")
