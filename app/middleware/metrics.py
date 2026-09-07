# -*- coding: utf-8 -*-
"""
Metrics Middleware - Збір метрик продуктивності
"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Optional
from datetime import datetime

from app.database import SessionLocal
from app.models.request import Request as RequestModel
from app.core.config import settings

logger = logging.getLogger("star_agents")

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware для збору метрик продуктивності"""
    
    def __init__(self, app, skip_paths: Optional[list] = None):
        super().__init__(app)
        self.skip_paths = skip_paths or [
            "/health",
            "/metrics",
            "/favicon.ico",
            "/static",
            "/assets",
            "/css",
            "/js"
        ]
        self.enabled = settings.ENABLE_METRICS if hasattr(settings, 'ENABLE_METRICS') else True
    
    async def dispatch(self, request: Request, call_next):
        # Пропускаємо запити, які не треба логувати
        if self._should_skip(request.url.path):
            return await call_next(request)
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Зберігаємо метрики асинхронно
            if self.enabled:
                await self._save_metrics(request, response, process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            if self.enabled:
                await self._save_error_metrics(request, str(e), process_time)
            raise
    
    async def _save_metrics(self, request: Request, response: Response, process_time: float):
        """Зберегти метрики запиту"""
        try:
            db = SessionLocal()
            
            # Отримуємо user_id з токена якщо є
            user_id = await self._get_user_id_from_request(request)
            
            req_log = RequestModel(
                path=request.url.path,
                method=request.method,
                response_time=process_time,
                status_code=response.status_code,
                user_agent=request.headers.get("user-agent", ""),
                ip=request.client.host if request.client else "unknown",
                user_id=user_id,
                created_at=datetime.utcnow()
            )
            
            db.add(req_log)
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    async def _save_error_metrics(self, request: Request, error: str, process_time: float):
        """Зберегти метрики помилки"""
        try:
            db = SessionLocal()
            
            req_log = RequestModel(
                path=request.url.path,
                method=request.method,
                response_time=process_time,
                status_code=500,
                user_agent=request.headers.get("user-agent", ""),
                ip=request.client.host if request.client else "unknown",
                user_id=None,
                created_at=datetime.utcnow()
            )
            
            db.add(req_log)
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to save error metrics: {e}")
    
    async def _get_user_id_from_request(self, request: Request) -> Optional[int]:
        """Отримати user_id з токена авторизації"""
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            # Тут можна декодувати JWT токен
            # Або просто повернути None якщо не потрібно
            return None
            
        except Exception:
            return None
    
    def _should_skip(self, path: str) -> bool:
        """Перевіряє чи потрібно пропустити цей шлях"""
        return any(path.startswith(skip_path) for skip_path in self.skip_paths)