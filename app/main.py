from app.core.config import settings
print(">>> USING DATABASE:", settings.DATABASE_URL)

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil

# === Ініціалізація FastAPI ===
app = FastAPI(
    title="Star Agents API",
    version="1.0.0",
    description="API для керування користувачами, агентами, покупками та балансом",
    debug=settings.DEBUG,
)

# === STATIC FILES ===
app.mount("/static", StaticFiles(directory="static"), name="static")

# === API ROUTERS ===
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.agents import router as agents_router
from app.api.v1.purchases import router as purchases_router
from app.api.v1.balance import router as balance_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.seed import router as seed_router
from app.api.v1.chat import router as chat_router

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(agents_router)
app.include_router(purchases_router)
app.include_router(balance_router)
app.include_router(analytics_router)
app.include_router(seed_router)
app.include_router(chat_router)

# === Jinja2 templates ===
templates = Jinja2Templates(directory="templates")

# === SYSTEM ROUTES ===
@app.get("/health")
def health():
    return {"status": "ok", "debug": settings.DEBUG}

# === FRONTEND ROUTES ===

@app.get("/", response_class=HTMLResponse)
def landing_page():
    return FileResponse("static/login.html")

@app.get("/login")
def login_redirect():
    return RedirectResponse(url="/")

@app.get("/agents", response_class=HTMLResponse)
def agents_page():
    return FileResponse("static/agents.html")

@app.get("/purchases", response_class=HTMLResponse)
def purchases_page():
    return FileResponse("static/purchases.html")

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard():
    return FileResponse("static/admin_dashboard_v10.html")

@app.get("/chat-ui", response_class=HTMLResponse)
def chat_ui():
    return FileResponse("static/chat.html")

# === Upload ===
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    with open(f"uploaded_{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"detail": f"File {file.filename} uploaded successfully"}

# === Demo agents ===
@app.get("/featured_agents")
def featured_agents():
    return [
        {"name": "SEO Agent", "skills": "SEO, Keywords, Analytics"},
        {"name": "Marketing Agent", "skills": "Ads, Social Media, Targeting"},
        {"name": "Analytics Agent", "skills": "Reports, BI, Forecasting"},
    ]
