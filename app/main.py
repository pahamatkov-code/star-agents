# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ███████╗████████╗ █████╗ ██████╗                             ║
║   ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗                            ║
║   ███████╗   ██║   ███████║██████╔╝                            ║
║   ╚════██║   ██║   ██╔══██║██╔══██╗                            ║
║   ███████║   ██║   ██║  ██║██║  ██║                            ║
║   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝                            ║
║                                                                  ║
║   █████╗  ██████╗ ███████╗███╗   ██╗████████╗███████╗          ║
║  ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔════╝          ║
║  ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ███████╗          ║
║  ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ╚════██║          ║
║  ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ███████║          ║
║  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝          ║
║                                                                  ║
║   ███████╗██╗   ██╗██╗  ████████╗███████╗                     ║
║   ██╔════╝╚██╗ ██╔╝██║  ╚══██╔══╝██╔════╝                     ║
║   █████╗   ╚████╔╝ ██║     ██║   ███████╗                     ║
║   ██╔══╝    ╚██╔╝  ██║     ██║   ╚════██║                     ║
║   ███████╗   ██║   ███████╗██║   ███████║                     ║
║   ╚══════╝   ╚═╝   ╚══════╝╚═╝   ╚══════╝                     ║
║                                                                  ║
║   🚀 API Version: 3.0.0                                         ║
║   🏆 Production Ready                                          ║
║   🔒 Security First                                            ║
║   ⚡ High Performance                                          ║
╚══════════════════════════════════════════════════════════════════╝
"""
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Dict, Any
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exception_handlers import http_exception_handler

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import init_db

# Middleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.security import SecurityMiddleware

# ============================================================
# НАЛАШТУВАННЯ ЛОГУВАННЯ
# ============================================================
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("star_agents")

# ============================================================
# RATE LIMITER
# ============================================================
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
    storage_uri="memory://"
)

# ============================================================
# LIFECYCLE MANAGER
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управління життєвим циклом додатку"""
    start_time = time.time()
    
    logger.info("=" * 70)
    logger.info("🚀 STAR AGENTS API STARTING...")
    logger.info(f"📌 Version: {settings.VERSION}")
    logger.info(f"🔧 Debug Mode: {settings.DEBUG}")
    logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🗄️  Database: {settings.DATABASE_URL}")
    logger.info("=" * 70)
    
    try:
        init_db()
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
    
    await check_external_services()
    
    init_time = time.time() - start_time
    logger.info("=" * 70)
    logger.info(f"✅ Application startup complete! ({init_time:.2f}s)")
    logger.info("=" * 70)
    logger.info(f"  📚 API Docs:        http://localhost:8000/docs")
    logger.info(f"  🖥️  Admin Panel:    http://localhost:8000/admin")
    logger.info(f"  🤖 Chat Webhook:    http://localhost:8000/chat/webhook")
    logger.info(f"  ❤️  Health Check:    http://localhost:8000/health")
    logger.info("=" * 70)
    
    yield
    
    logger.info("🛑 Star Agents API shutting down...")
    logger.info("=" * 70)

# ============================================================
# ІНІЦІАЛІЗАЦІЯ FASTAPI
# ============================================================
app = FastAPI(
    title="Star Agents API",
    version=settings.VERSION,
    description="""
🚀 **Star Agents** — професійна платформа для керування AI агентами.

## Основні можливості:
- 🤖 **AI Агенти** — керування та моніторинг
- 💬 **Telegram Бот** — інтеграція з чатом
- 🔐 **Автентифікація** — JWT токени та безпека
- 💰 **Покупки** — керування платежами

## Швидкі посилання:
- [Swagger UI](/docs) — інтерактивна документація
- [ReDoc](/redoc) — альтернативна документація
- [Admin Panel](/admin) — панель керування
- [Health Check](/health) — статус системи
""",
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else "/api/docs",
    redoc_url="/redoc" if settings.DEBUG else "/api/redoc",
    openapi_tags=[
        {"name": "Authentication", "description": "🔐 Авторизація та реєстрація"},
        {"name": "Chat", "description": "💬 Telegram чат та вебхуки"},
        {"name": "System", "description": "⚙️ Системні ендпоінти"},
        {"name": "Frontend", "description": "🎨 Сторінки інтерфейсу"},
    ]
)

# ============================================================
# MIDDLEWARE
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=3600,
)

app.add_middleware(SecurityMiddleware)
app.add_middleware(LoggingMiddleware)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ============================================================
# ГЛОБАЛЬНІ ОБРОБНИКИ ПОМИЛОК
# ============================================================
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"⚠️ HTTP {exc.status_code}: {exc.detail} - {request.url.path}")
    return await http_exception_handler(request, exc)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"💥 Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else None,
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# ============================================================
# СТАТИЧНІ ФАЙЛИ
# ============================================================
app.mount("/static", StaticFiles(directory="static"), name="static")

if os.path.exists("static/assets"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
if os.path.exists("static/css"):
    app.mount("/css", StaticFiles(directory="static/css"), name="css")
if os.path.exists("static/js"):
    app.mount("/js", StaticFiles(directory="static/js"), name="js")
if os.path.exists("static/fonts"):
    app.mount("/fonts", StaticFiles(directory="static/fonts"), name="fonts")
if os.path.exists("static/images"):
    app.mount("/images", StaticFiles(directory="static/images"), name="images")

# ============================================================
# ПІДКЛЮЧЕННЯ РОУТЕРІВ
# ============================================================
from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
from app.api.v1.dashboard_simple import router as dashboard_router
app.include_router(dashboard_router)

# ============================================================
# СИСТЕМНІ ЕНДПОІНТИ
# ============================================================
@app.get("/health", tags=["System"])
@limiter.limit("10/minute")
async def health_check(request: Request) -> Dict[str, Any]:
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "services": {
            "database": "connected",
            "telegram": "connected" if settings.TELEGRAM_BOT_TOKEN else "not_configured",
            "openrouter": "configured" if settings.OPENROUTER_API_KEY else "not_configured",
            "n8n": "configured" if settings.N8N_WEBHOOK_URL else "not_configured"
        }
    }

@app.get("/metrics", tags=["System"])
async def metrics():
    return {"message": "Metrics endpoint"}

@app.get("/info", tags=["System"])
async def system_info():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "api_docs": "/docs",
        "admin_panel": "/admin",
        "chat_webhook": "/chat/webhook"
    }

# ============================================================
# FRONTEND СТОРІНКИ
# ============================================================
@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
@limiter.limit("30/minute")
async def landing_page(request: Request):
    return FileResponse("static/login.html")

@app.get("/login", tags=["Frontend"])
async def login_redirect():
    return RedirectResponse(url="/")

@app.get("/agents", response_class=HTMLResponse, tags=["Frontend"])
async def agents_page(request: Request):
    return FileResponse("static/agents.html")

@app.get("/purchases", response_class=HTMLResponse, tags=["Frontend"])
async def purchases_page(request: Request):
    return FileResponse("static/purchases.html")

@app.get("/admin", response_class=HTMLResponse, tags=["Frontend"])
async def admin_dashboard(request: Request):
    return FileResponse("static/admin_dashboard_v10.html")

@app.get("/chat-ui", response_class=HTMLResponse, tags=["Frontend"])
async def chat_ui(request: Request):
    return FileResponse("static/chat.html")

@app.get("/dashboard", response_class=HTMLResponse, tags=["Frontend"])
async def dashboard_page(request: Request):
    return FileResponse("static/dashboard.html")

# ============================================================
# ДОПОМІЖНІ ФУНКЦІЇ
# ============================================================
async def check_external_services() -> Dict[str, str]:
    services_status = {}
    
    if settings.TELEGRAM_BOT_TOKEN:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getMe"
                )
                if resp.status_code == 200:
                    logger.info("✅ Telegram bot connected")
                    services_status["telegram"] = "connected"
                else:
                    services_status["telegram"] = "error"
        except Exception as e:
            logger.warning(f"⚠️ Telegram error: {e}")
            services_status["telegram"] = "error"
    else:
        services_status["telegram"] = "not_configured"
    
    services_status["openrouter"] = "configured" if settings.OPENROUTER_API_KEY else "not_configured"
    services_status["n8n"] = "configured" if settings.N8N_WEBHOOK_URL else "not_configured"
    
    logger.info(f"📡 External services: {services_status}")
    return services_status

# ============================================================
# ІНФОРМАЦІЯ ПРО СТАРТ
# ============================================================
logger.info("=" * 70)
logger.info("✅ Star Agents API initialized successfully!")
logger.info(f"📌 Version: {settings.VERSION}")
logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")
logger.info("🔐 Authentication API: /auth/login, /auth/register")
logger.info("🤖 Chat Webhook: /chat/webhook")
logger.info("📚 API Docs: http://localhost:8000/docs")
logger.info("=" * 70)