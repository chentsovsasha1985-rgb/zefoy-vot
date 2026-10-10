FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    tesseract-ocr \
    git \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

COPY requirements.txt .
COPY main.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py", "--headless", "--auto-captcha", "--service", "hearts", "https://vt.tiktok.com/ZSb71qRVt/"]
