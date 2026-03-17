# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# System dependencies for Playwright + newspaper3k + lxml
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Cache mount mantém o download do pip entre builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install "feedparser>=6.0.0" && \
    pip install --no-deps pygooglenews && \
    pip install dateparser && \
    pip install -r requirements.txt && \
    pip install gunicorn

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

EXPOSE 5000

CMD ["gunicorn", "api.wsgi:application", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120"]
