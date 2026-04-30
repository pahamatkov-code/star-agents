FROM python:3.12-slim

WORKDIR /app

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir uvicorn[standard] crewai

COPY . .

EXPOSE 8001

# Запускаємо агент на порту 8001, щоб не конфліктувати з основним API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]