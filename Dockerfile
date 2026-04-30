# Використовуємо офіційний Python-образ
FROM python:3.12-slim

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файл залежностей
COPY requirements.txt .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код агента
COPY . .

# Відкриваємо порт
EXPOSE 8000

# Команда запуску
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
