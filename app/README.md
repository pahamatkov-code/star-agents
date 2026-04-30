🌟 Star Agents — AI‑Powered E‑commerce Support Platform

Modern FastAPI backend + animated floating chat widget + rule‑based support agent

<p align="center">

<img src="https://img.shields.io/badge/Python-3.10+-blue" />

<img src="https://img.shields.io/badge/FastAPI-Framework-009688" />

<img src="https://img.shields.io/badge/TailwindCSS-UI-38B2AC" />

<img src="https://img.shields.io/badge/Status-MVP-green" />

<img src="https://img.shields.io/badge/License-MIT-yellow" />

</p>



🚀 Overview

Star Agents — це сучасна платформа для e‑commerce підтримки, побудована на FastAPI, з красивим, анімованим, інтерактивним чат‑віджетом, який виглядає як у Shopify, Intercom або Crisp.



Проєкт включає:



повноцінний бекенд (авторизація, ролі, агенти, покупки, баланс, аналітика)



rule‑based чат‑агента



сучасний UI‑чат з анімаціями



плаваючий віджет чату



темну/світлу тему



плавні анімації, аватарки, typing‑indicator



готову структуру для розширення AI‑агентом (OpenAI / CrewAI)



Це MVP рівня SaaS‑продукту, який можна демонструвати рекрутерам, клієнтам або використовувати як основу для комерційного сервісу.



✨ Features

🔐 Authentication \& Roles

JWT авторизація



Ролі: admin, user



Захищені маршрути



👤 Users \& Agents

CRUD для користувачів



CRUD для агентів



Демонстраційні агенти



💳 Balance \& Purchases

Поповнення балансу



Створення покупок



Історія транзакцій



📊 Analytics

API для аналітики



Готова інтеграція з адмін‑панеллю



💬 Rule‑Based Chat Agent

Ендпоінт /chat



Ендпоінт /chat/reset



Збереження контексту діалогу



Готова структура для AI‑агента



🎨 Modern Chat UI (Frontend)

✔ Плаваючий віджет чату (як у Shopify / Intercom)

Кнопка 💬 у правому нижньому куті



Анімація відкриття/закриття



Повністю адаптивний



✔ Аватарки (user + agent)

DiceBear генерація



Красиві, чисті, сучасні



✔ Анімації

Fade‑in для повідомлень



Fade‑in / fade‑out для typing‑indicator



Bounce‑dots typing



Smooth scroll



✔ Темна/світла тема

Перемикач теми



Збереження в localStorage



✔ Чистий Tailwind‑дизайн

Мінімалістично



Акуратно



Професійно



🏗 Tech Stack

Backend

Python 3.10+



FastAPI



Pydantic



SQLAlchemy



Alembic



JWT (PyJWT)



Uvicorn



Frontend

HTML + TailwindCSS



Vanilla JavaScript



Floating widget UI



Анімації (CSS + JS)



Database

PostgreSQL / SQLite (локально)



📁 Project Structure

Код

app/

&#x20;├── api/v1/

&#x20;│    ├── auth.py

&#x20;│    ├── users.py

&#x20;│    ├── agents.py

&#x20;│    ├── purchases.py

&#x20;│    ├── balance.py

&#x20;│    ├── analytics.py

&#x20;│    ├── chat.py

&#x20;│    └── seed.py

&#x20;├── core/

&#x20;├── models/

&#x20;├── main.py

&#x20;└── ...

static/

&#x20;├── chat.html

&#x20;├── login.html

&#x20;├── admin\_dashboard\_v10.html

&#x20;└── ...

templates/

requirements.txt

README.md

▶️ Running Locally

1\. Clone the repo

bash

git clone https://github.com/your-username/star-agents.git

cd star-agents

2\. Create virtual environment

bash

python -m venv venv

source venv/bin/activate  # Linux/Mac

venv\\Scripts\\activate     # Windows

3\. Install dependencies

bash

pip install -r requirements.txt

4\. Run server

bash

uvicorn app.main:app --reload

5\. Open in browser

Код

http://127.0.0.1:8000/chat-ui

📸 Screenshots

Додай свої скріни у папку docs/ і встав сюди:



Код

docs/

&#x20;├── chat-dark.png

&#x20;├── chat-light.png

&#x20;├── widget.png

&#x20;├── typing.png

&#x20;└── admin.png

Галерея:

Dark Theme	Light Theme

\[Похоже, результат оказался небезопасным для отображения. Давайте внесем изменения и попробуем что-нибудь другое!]	\[Похоже, результат оказался небезопасным для отображения. Давайте внесем изменения и попробуем что-нибудь другое!]





Floating Widget	Typing Indicator

\[Похоже, результат оказался небезопасным для отображения. Давайте внесем изменения и попробуем что-нибудь другое!]	\[Похоже, результат оказался небезопасным для отображения. Давайте внесем изменения и попробуем что-нибудь другое!]





🧭 Roadmap

\[ ] AI‑агент (OpenAI / CrewAI)



\[ ] WebSocket real‑time чат



\[ ] Інтеграція Nova Poshta API



\[ ] Push‑повідомлення



\[ ] SaaS‑панель для клієнтів



\[ ] Docker‑деплой



🤝 Contributing

Pull requests welcome.

Для великих змін — відкрий issue.



📄 License

MIT License.



👤 Author

Pavlo Matkovskyi  

Backend Engineer \& Product Builder

Ukraine 🇺🇦

