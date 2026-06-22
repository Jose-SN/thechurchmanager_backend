# Use a lightweight Python image
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Settings load from .env at runtime (app/core/config.py). Do not put secrets in ENV here.
# .env is included when present in the build context (local docker build).
# On Railway, set the same keys as service Variables — they override .env at runtime.
COPY . .

ENV PORT=8080

EXPOSE 8080

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port 8080"]
