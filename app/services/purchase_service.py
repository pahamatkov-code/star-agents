from sqlalchemy.orm import Session

from app.models.user import User
from app.models.agent import Agent
from app.models.purchase import Purchase
from app.models.balance_transaction import BalanceTransaction

from app.schemas.purchase import PurchaseCreate, PurchaseUpdate


class PurchaseService:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------
    # CREATE PURCHASE (user → тільки для себе, admin → для всіх)
    # ---------------------------------------------------
    def create_purchase(self, data: PurchaseCreate, current_user):
        """
        User може створювати покупку тільки для себе.
        Admin може створювати покупку для будь-якого user_id.
        """

        # User може купувати тільки для себе
        if current_user.role != "admin":
            data.user_id = current_user.id

        # Перевіряємо користувача
        user = self.db.query(User).filter(User.id == data.user_id).first()
        if not user:
            return None, "User not found"

        # Перевіряємо агента
        agent = self.db.query(Agent).filter(Agent.id == data.agent_id).first()
        if not agent:
            return None, "Agent not found"

        # Ціна агента
        price = agent.price
        if price <= 0:
            return None, "Invalid agent price"

        # Перевірка балансу (тільки для user)
        if current_user.role != "admin":
            if user.balance < price:
                return None, "Insufficient balance"

        # -----------------------------------------
        # Списання балансу (тільки для user)
        # -----------------------------------------
        if current_user.role != "admin":
            user.balance -= price
            self.db.commit()
            self.db.refresh(user)

        # -----------------------------------------
        # Лог транзакції
        # -----------------------------------------
        transaction = BalanceTransaction(
            user_id=user.id,
            amount=-price,
            type="purchase"
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)

        # -----------------------------------------
        # Створення покупки
        # -----------------------------------------
        purchase = Purchase(
            user_id=user.id,
            agent_id=agent.id,
            price=price
        )

        self.db.add(purchase)
        self.db.commit()
        self.db.refresh(purchase)

        return purchase, None

    # ---------------------------------------------------
    # GET PURCHASE BY ID
    # ---------------------------------------------------
    def get_purchase(self, purchase_id: int):
        return (
            self.db.query(Purchase)
            .filter(Purchase.id == purchase_id)
            .first()
        )

    # ---------------------------------------------------
    # GET ALL PURCHASES (admin)
    # ---------------------------------------------------
    def get_all(self):
        return self.db.query(Purchase).all()

    # ---------------------------------------------------
    # GET PURCHASES OF CURRENT USER
    # ---------------------------------------------------
    def get_user_purchases(self, user_id: int):
        return (
            self.db.query(Purchase)
            .filter(Purchase.user_id == user_id)
            .all()
        )

    # ---------------------------------------------------
    # UPDATE PURCHASE (admin only)
    # ---------------------------------------------------
    def update_purchase(self, purchase_id: int, data: PurchaseUpdate):
        purchase = self.get_purchase(purchase_id)
        if not purchase:
            return None, "Purchase not found"

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(purchase, key, value)

        self.db.commit()
        self.db.refresh(purchase)
        return purchase, None

    # ---------------------------------------------------
    # DELETE PURCHASE (admin only)
    # ---------------------------------------------------
    def delete_purchase(self, purchase_id: int):
        purchase = self.get_purchase(purchase_id)
        if not purchase:
            return None, "Purchase not found"

        self.db.delete(purchase)
        self.db.commit()
        return True, None
