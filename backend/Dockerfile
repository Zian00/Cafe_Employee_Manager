FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=120 -r requirements.txt

COPY . .

EXPOSE 8000

CMD sh -c "alembic upgrade head && exec uvicorn app.api.main:app --host 0.0.0.0 --port \${PORT:-8000} \${RELOAD:+--reload}"
