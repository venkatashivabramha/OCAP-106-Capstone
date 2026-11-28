FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY frontend/isl-chat-ui/dist/ ./frontend/isl-chat-ui/dist/

WORKDIR /app/backend

# Collect static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD python manage.py migrate --noinput && \
    daphne -b 0.0.0.0 -p ${PORT:-8000} config.asgi:application
