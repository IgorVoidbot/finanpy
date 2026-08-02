FROM python:3.12-slim

# Evita .pyc no container e garante logs sem buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DB_PATH=/app/data/db.sqlite3

WORKDIR /app

# Instala as dependencias primeiro para aproveitar o cache de camadas
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Diretorio do banco SQLite (montado como volume no docker-compose)
# e usuario sem privilegios de root
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]
