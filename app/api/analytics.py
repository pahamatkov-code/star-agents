# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.chat import ChatMessage

logger = logging.getLogger("star_agents")
router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

INTENT_COLORS = ["#EC4899", "#8B5CF6", "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#6366F1", "#14B8A6", "#F472B6", "#34D399"]
RECENT_MESSAGES_LIMIT = 20


@router.get("/dashboard")
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📊 Отримати дані для дашборду"""
    try:
        total_requests = db.query(ChatMessage).count()
        total_users = db.query(User).count()
        total_errors = db.query(ChatMessage).filter(ChatMessage.status == "error").count()
        avg_time = db.query(func.avg(ChatMessage.response_time)).scalar() or 0.0

        # Інтенти
        intents_data = db.query(
            ChatMessage.intent,
            func.count(ChatMessage.id).label('count')
        ).filter(ChatMessage.intent.isnot(None))\
         .group_by(ChatMessage.intent)\
         .order_by(desc('count'))\
         .all()

        intents = {i: c for i, c in intents_data if i}
        colors = {}
        for idx, intent in enumerate(intents.keys()):
            colors[intent] = {
                "count": intents[intent],
                "color": INTENT_COLORS[idx % len(INTENT_COLORS)]
            }

        # Останні повідомлення
        recent = db.query(ChatMessage).order_by(desc(ChatMessage.created_at)).limit(RECENT_MESSAGES_LIMIT).all()
        recent_messages = [{
            "message": (msg.message or "")[:50] + ("..." if len(msg.message or "") > 50 else ""),
            "time": msg.created_at.strftime("%H:%M") if msg.created_at else "",
            "datetime": msg.created_at.isoformat() if msg.created_at else None,
            "user_id": msg.user_id,
            "intent": msg.intent,
            "status": msg.status or "success"
        } for msg in recent]

        return {
            "requests": total_requests,
            "avg_time": round(float(avg_time), 2),
            "errors": total_errors,
            "users": total_users,
            "revenue": 0.0,
            "intents": intents,
            "intents_colors": colors,
            "top_agents": [],
            "top_users": [],
            "timeline": [],
            "recent_messages": recent_messages,
            "meta": {
                "generated_at": datetime.utcnow().isoformat(),
                "user": current_user.email,
                "cache": "fresh",
                "version": "3.0.0"
            }
        }
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/realtime")
async def get_realtime(db: Session = Depends(get_db)):
    """⚡ Метрики в реальному часі"""
    last_minute = datetime.utcnow() - timedelta(minutes=1)
    requests_1m = db.query(ChatMessage).filter(ChatMessage.created_at >= last_minute).count()
    return {
        "requests_1m": requests_1m,
        "requests_1h": 0,
        "requests_per_second": round(requests_1m / 60, 2),
        "active_users": 0,
        "last_request_time": None,
        "last_request_user": None
    }


@router.get("/timeline")
async def get_timeline(hours: int = 24, db: Session = Depends(get_db)):
    """📈 Динаміка запитів"""
    h_ago = datetime.utcnow() - timedelta(hours=min(hours, 168))
    data = db.query(
        func.date_trunc('hour', ChatMessage.created_at).label('hour'),
        func.count(ChatMessage.id).label('count')
    ).filter(ChatMessage.created_at >= h_ago)\
     .group_by('hour')\
     .order_by('hour')\
     .all()

    return {
        "data": [{"hour": h.strftime("%H:00"), "count": c} for h, c in data],
        "total": sum(c for _, c in data),
        "max": max([c for _, c in data]) if data else 0,
        "avg": round(sum(c for _, c in data) / len(data), 2) if data else 0,
        "trend": "up" if data else "neutral"
    }


@router.get("/health")
async def analytics_health():
    """❤️ Перевірка здоров'я аналітики"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}