# app/services/analytics_service.py
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.purchase import Purchase
from app.models.balance_transaction import BalanceTransaction
from app.models.user import User
from app.models.agent import Agent
from app.models.intents_log import IntentsLog


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------
    # PURCHASE ANALYTICS
    # ---------------------------------------------------
    def get_purchase_analytics(self) -> Dict[str, Any]:
        total_purchases = self.db.query(func.count(Purchase.id)).scalar() or 0
        total_revenue = self.db.query(func.coalesce(func.sum(Purchase.price), 0.0)).scalar() or 0.0
        unique_users = self.db.query(func.count(func.distinct(Purchase.user_id))).scalar() or 0

        purchases_by_day = (
            self.db.query(
                func.date(Purchase.created_at).label("day"),
                func.count(Purchase.id).label("count"),
                func.coalesce(func.sum(Purchase.price), 0.0).label("revenue")
            )
            .group_by(func.date(Purchase.created_at))
            .order_by(func.date(Purchase.created_at))
            .all()
        )

        top_agents = (
            self.db.query(
                Agent.name,
                func.count(Purchase.id).label("count"),
                func.coalesce(func.sum(Purchase.price), 0.0).label("revenue")
            )
            .join(Agent, Agent.id == Purchase.agent_id)
            .group_by(Agent.id, Agent.name)
            .order_by(func.sum(Purchase.price).desc())
            .limit(5)
            .all()
        )

        top_users = (
            self.db.query(
                User.email,
                func.count(Purchase.id).label("count"),
                func.coalesce(func.sum(Purchase.price), 0.0).label("spent")
            )
            .join(User, User.id == Purchase.user_id)
            .group_by(User.id, User.email)
            .order_by(func.sum(Purchase.price).desc())
            .limit(5)
            .all()
        )

        return {
            "total_purchases": total_purchases,
            "total_revenue": float(total_revenue),
            "unique_users": unique_users,
            "purchases_by_day": [
                {"day": str(day), "count": count, "revenue": float(revenue or 0.0)}
                for day, count, revenue in purchases_by_day
            ],
            "top_agents": [
                {"agent": name, "count": count, "revenue": float(revenue or 0.0)}
                for name, count, revenue in top_agents
            ],
            "top_users": [
                {"user": email, "count": count, "spent": float(spent or 0.0)}
                for email, count, spent in top_users
            ],
        }

    # ---------------------------------------------------
    # BALANCE ANALYTICS
    # ---------------------------------------------------
    def get_balance_analytics(self) -> Dict[str, Any]:
        total_topups = (
            self.db.query(func.coalesce(func.sum(BalanceTransaction.amount), 0.0))
            .filter(BalanceTransaction.type == "topup")
            .scalar() or 0.0
        )

        total_spent = (
            self.db.query(func.coalesce(func.sum(BalanceTransaction.amount), 0.0))
            .filter(BalanceTransaction.type == "spend")
            .scalar() or 0.0
        )

        net_flow = total_topups + total_spent  # spend від’ємне або нуль

        topups_by_day = (
            self.db.query(
                func.date(BalanceTransaction.created_at),
                func.coalesce(func.sum(BalanceTransaction.amount), 0.0)
            )
            .filter(BalanceTransaction.type == "topup")
            .group_by(func.date(BalanceTransaction.created_at))
            .order_by(func.date(BalanceTransaction.created_at))
            .all()
        )

        expenses_by_day = (
            self.db.query(
                func.date(BalanceTransaction.created_at),
                func.coalesce(func.sum(BalanceTransaction.amount), 0.0)
            )
            .filter(BalanceTransaction.type == "spend")
            .group_by(func.date(BalanceTransaction.created_at))
            .order_by(func.date(BalanceTransaction.created_at))
            .all()
        )

        return {
            "total_topups": float(total_topups),
            "total_spent": float(total_spent),
            "net_flow": float(net_flow),
            "topups_by_day": [
                {"day": str(day), "amount": float(amount or 0.0)}
                for day, amount in topups_by_day
            ],
            "expenses_by_day": [
                {"day": str(day), "amount": float(amount or 0.0)}
                for day, amount in expenses_by_day
            ],
        }

    # ---------------------------------------------------
    # INTENTS ANALYTICS
    # ---------------------------------------------------
    def get_intents_distribution(self) -> Dict[str, int]:
        rows = (
            self.db.query(IntentsLog.intent, func.count(IntentsLog.id))
            .group_by(IntentsLog.intent)
            .all()
        )
        return {intent: count for intent, count in rows if intent}

    def get_intents_summary(self) -> Dict[str, Any]:
        total_intents = self.db.query(func.count(IntentsLog.id)).scalar() or 0
        errors = (
            self.db.query(func.count(IntentsLog.id))
            .filter(IntentsLog.message.ilike("%Помилка%"))
            .scalar() or 0
        )
        return {
            "total_intents": total_intents,
            "errors": errors,
            "distribution": self.get_intents_distribution()
        }

    # ---------------------------------------------------
    # MAIN DASHBOARD DTO
    # ---------------------------------------------------
    def get_dashboard(self) -> Dict[str, Any]:
        purchases = self.get_purchase_analytics()
        balance = self.get_balance_analytics()
        intents = self.get_intents_summary()

        total_users = self.db.query(func.count(User.id)).scalar() or 0

        return {
            "requests": intents["total_intents"],
            "avg_time": 0.24,
            "errors": intents["errors"],
            "users": total_users,
            "revenue": purchases["total_revenue"],
            "intents": intents["distribution"],
            "top_agents": purchases["top_agents"],
            "top_users": purchases["top_users"],
            "details": {
                "purchases": purchases,
                "balance": balance
            }
        }