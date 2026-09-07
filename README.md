# 🤖 Star Agents

**AI-powered customer support platform for e-commerce**

[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.115+-green)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-3.0.0-orange)](https://github.com/pahamatkov-code/star-agents)

---

## 🚀 Overview

Star Agents is a production-ready AI system that automates customer support for e-commerce businesses via Telegram bot with LLM-powered intent recognition and provides real-time analytics dashboard.

**Key features:**
- ⚡ Fast responses (AI-powered)
- 📊 Real-time analytics dashboard
- 🎯 Intent classification (8 business intents)
- 🔄 Automatic handover to human agent

---

## 🧠 Features

### 🤖 AI Telegram Bot
- Natural language responses (Ukrainian/English)
- Intent classification (delivery, payment, returns, warranty, etc.)
- Automatic handover to human agent for complex cases

### 📊 Admin Dashboard
- Real-time request analytics
- Intent distribution chart (doughnut)
- Live feed of customer interactions
- Top agents and user statistics
- Dark/light theme support

### ⚙️ Technical Stack
- **Backend:** FastAPI, SQLAlchemy, Pydantic
- **Database:** PostgreSQL, Redis
- **AI:** OpenRouter API (Claude, Gemini)
- **Infrastructure:** Docker, Docker Compose
- **Frontend:** Tailwind CSS, Chart.js

---

## 🛠️ Installation

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- PostgreSQL (or use Docker container)
- Telegram Bot Token (from @BotFather)
- OpenRouter API Key

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/pahamatkov-code/star-agents.git
cd star-agents

# 2. Copy environment variables
cp .env.example .env
# Edit .env with your keys

# 3. Run with Docker
docker compose up --build

# 4. Access
# API: http://localhost:8000
# Dashboard: http://localhost:8000/admin
# API Docs: http://localhost:8000/docs
star-agents/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Config, database, security
│   ├── models/          # SQLAlchemy models
│   ├── services/        # Business logic
│   ├── agents/          # AI intent classification
│   └── middleware/      # Logging, security, metrics
├── static/              # Frontend (dashboard)
├── docker-compose.yml   # Infrastructure
├── Dockerfile          # Application container
├── requirements.txt    # Python dependencies
└── .env.example        # Environment variables template
📊 Demo
🎥 Watch 60-second demo: LinkedIn Video

📄 License
This project is licensed under the MIT License.

📬 Contact
Pavlo Matkovskyi

Email: pahamatkov@gmail.com

Telegram: @pavelMatkov

LinkedIn: pavel-matkovsky

⭐ Support
If you find this project useful, please consider giving it a star ⭐ on GitHub.

