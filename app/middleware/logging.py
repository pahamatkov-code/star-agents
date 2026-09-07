# -*- coding: utf-8 -*-
"""
Logging Middleware - Детальне логування всіх запитів
"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Optional

logger = logging.getLogger("star_agents")

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логування запитів"""
    
    async def dispatch(self, request: Request, call_next):
        # Пропускаємо статику та healthcheck
        if self._should_skip_logging(request.url.path):
            return await call_next(request)
        
        start_time = time.time()
        
        # Отримуємо інформацію про запит
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        query = str(request.query_params) if request.query_params else ""
        
        # Логуємо вхідний запит
        logger.info(f"➡️  {method} {path}{'?' + query if query else ''} from {client_ip}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Логуємо відповідь
            log_level = logging.INFO
            if response.status_code >= 500:
                log_level = logging.ERROR
            elif response.status_code >= 400:
                log_level = logging.WARNING
            
            logger.log(
                log_level,
                f"⬅️  {method} {path} → {response.status_code} ({process_time:.3f}s)"
            )
            
            # Додаємо час виконання в заголовки
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"❌ {method} {path} → ERROR: {str(e)} ({process_time:.3f}s)")
            raise
    
    def _should_skip_logging(self, path: str) -> bool:
        """Перевіряє чи потрібно логувати цей шлях"""
        skip_paths = [
            "/health",
            "/metrics",
            "/favicon.ico",
            "/robots.txt",
            "/static",
            "/assets",
            "/css",
            "/js"
        ]
        return any(path.startswith(skip_path) for skip_path in skip_paths)