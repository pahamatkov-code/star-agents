# -*- coding: utf-8 -*-
"""
Security Middleware - Захист від загроз та безпечні заголовки
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger("star_agents")

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware для безпеки"""
    
    async def dispatch(self, request: Request, call_next):
        # Додаємо безпечні заголовки до відповіді
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS (тільки в продакшн)
        if not request.url.scheme == "http":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Захист від MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        return response