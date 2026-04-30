from sqlalchemy.orm import Session
from app.models.purchase import Purchase


class PurchaseRepository:
    def __init__(self, db: Session):
        self.db = db

    # Створення покупки
    def create(self, data: dict) -> Purchase:
        purchase = Purchase(**data)
        self.db.add(purchase)
        self.db.commit()
        self.db.refresh(purchase)
        return purchase

    # Отримати покупку за ID
    def get(self, purchase_id: int) -> Purchase | None:
        return (
            self.db.query(Purchase)
            .filter(Purchase.id == purchase_id)
            .first()
        )

    # Усі покупки
    def get_all(self):
        return self.db.query(Purchase).all()

    # Покупки одного користувача
    def get_by_user(self, user_id: int):
        return (
            self.db.query(Purchase)
            .filter(Purchase.user_id == user_id)
            .all()
        )

    # Оновлення покупки (тільки admin)
    def update(self, purchase: Purchase, data: dict) -> Purchase:
        for key, value in data.items():
            setattr(purchase, key, value)
        self.db.commit()
        self.db.refresh(purchase)
        return purchase

    # Видалення покупки (тільки admin)
    def delete(self, purchase: Purchase) -> bool:
        self.db.delete(purchase)
        self.db.commit()
        return True
