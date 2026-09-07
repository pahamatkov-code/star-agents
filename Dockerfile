# Використовуємо офіційний Python-образ
FROM python:3.12-slim

# Оновлюємо pip
RUN pip install --upgrade pip

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файл залежностей
COPY requirements.txt .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код проєкту
COPY . .

# ENV-змінні (можна перевизначати через docker-compose або docker run -e)
ENV TELEGRAM_BOT_TOKEN=""
ENV DATABASE_URL="sqlite:///./agents.db"

# Відкриваємо порт
EXPOSE 8000

# Команда запуску
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
