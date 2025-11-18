# Cloudflare Containers için optimize edilmiş Dockerfile
FROM python:3.11-slim

# Çalışma dizini
WORKDIR /app

# System dependencies (alfabetik sırada)
RUN apt-get update && apt-get install -y \
    g++ \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Log dizini oluştur
RUN mkdir -p /app/logs

# Port expose
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/').raise_for_status()" || exit 1

# Gunicorn ile çalıştır
CMD ["gunicorn", "-c", "gunicorn_config.py", "main:app"]
