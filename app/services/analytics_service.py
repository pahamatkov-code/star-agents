from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models.purchase import Purchase
from app.models.balance_transaction import BalanceTransaction
from app.models.user import User
from app.models.agent import Agent


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------
    # PURCHASE ANALYTICS
    # ---------------------------------------------------
    def get_purchase_analytics(self):
        total_purchases = self.db.query(func.count(Purchase.id)).scalar()
        total_revenue = self.db.query(func.sum(Purchase.price)).scalar() or 0
        unique_users = self.db.query(func.count(func.distinct(Purchase.user_id))).scalar()

        # Покупки по днях (останні 30 днів)
        purchases_by_day = (
            self.db.query(
                func.date(Purchase.created_at).label("day"),
                func.count(Purchase.id).label("count"),
                func.sum(Purchase.price).label("revenue")
            )
            .group_by(func.date(Purchase.created_at))
            .order_by(func.date(Purchase.created_at))
            .all()
        )

        # Топ агентів
        top_agents = (
            self.db.query(
                Agent.name,
                func.count(Purchase.id).label("count"),
                func.sum(Purchase.price).label("revenue")
            )
            .join(Agent, Agent.id == Purchase.agent_id)
            .group_by(Agent.id)
            .order_by(func.sum(Purchase.price).desc())
            .limit(5)
            .all()
        )

        # Топ користувачів
        top_users = (
            self.db.query(
                User.username,
                func.count(Purchase.id).label("count"),
                func.sum(Purchase.price).label("spent")
            )
            .join(User, User.id == Purchase.user_id)
            .group_by(User.id)
            .order_by(func.sum(Purchase.price).desc())
            .limit(5)
            .all()
        )

        return {
            "total_purchases": total_purchases,
            "total_revenue": float(total_revenue),
            "unique_users": unique_users,
            "purchases_by_day": [
                {"day": str(day), "count": count, "revenue": float(revenue)}
                for day, count, revenue in purchases_by_day
            ],
            "top_agents": [
                {"agent": name, "count": count, "revenue": float(revenue)}
                for name, count, revenue in top_agents
            ],
            "top_users": [
                {"user": username, "count": count, "spent": float(spent)}
                for username, count, spent in top_users
            ],
        }

    # ---------------------------------------------------
    # BALANCE ANALYTICS
    # ---------------------------------------------------
    def get_balance_analytics(self):
        total_topups = (
            self.db.query(func.sum(BalanceTransaction.amount))
            .filter(BalanceTransaction.type == "topup")
            .scalar()
            or 0
        )

        total_spent = (
            self.db.query(func.sum(BalanceTransaction.amount))
            .filter(BalanceTransaction.type == "purchase")
            .scalar()
            or 0
        )

        net_flow = total_topups + total_spent  # spent — від’ємне

        # Топапи по днях
        topups_by_day = (
            self.db.query(
                func.date(BalanceTransaction.created_at),
                func.sum(BalanceTransaction.amount)
            )
            .filter(BalanceTransaction.type == "topup")
            .group_by(func.date(BalanceTransaction.created_at))
            .order_by(func.date(BalanceTransaction.created_at))
            .all()
        )

        # Витрати по днях
        expenses_by_day = (
            self.db.query(
                func.date(BalanceTransaction.created_at),
                func.sum(BalanceTransaction.amount)
            )
            .filter(BalanceTransaction.type == "purchase")
            .group_by(func.date(BalanceTransaction.created_at))
            .order_by(func.date(BalanceTransaction.created_at))
            .all()
        )

        return {
            "total_topups": float(total_topups),
            "total_spent": float(total_spent),
            "net_flow": float(net_flow),
            "topups_by_day": [
                {"day": str(day), "amount": float(amount)}
                for day, amount in topups_by_day
            ],
            "expenses_by_day": [
                {"day": str(day), "amount": float(amount)}
                for day, amount in expenses_by_day
            ],
        }

    # ---------------------------------------------------
    # DASHBOARD (все разом)
    # ---------------------------------------------------
    def get_dashboard(self):
        return {
            "purchases": self.get_purchase_analytics(),
            "balance": self.get_balance_analytics(),
        }
