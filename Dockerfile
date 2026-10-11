# Используем официальный стабильный образ Python
FROM python:3.11-slim

# Устанавливаем системные библиотеки, без которых браузер не запустится в Linux
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую папку в контейнере
WORKDIR /app

# Копируем требования и устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скачиваем и устанавливаем браузер Chromium для работы автоматизации
RUN pip install playwright && playwright install chromium

# Копируем весь остальной код бота в контейнер
COPY . .

# Принудительно настраиваем пути поиска модулей для Python (включая корень и папку src)
ENV PYTHONPATH="/app:/app/src:${PYTHONPATH}"

# Команда для автоматического запуска бота с автоматическим поиском файла main.py
CMD ["sh", "-c", "if [ -f /app/src/main.py ]; then python /app/src/main.py; else python /app/main.py; fi"]
