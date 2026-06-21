# Use a lightweight Python image
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway injects PORT at runtime — do not hardcode the listen port in CMD.
# Set secrets (JWT_SECRET, DATABASE_URL, etc.) in Railway Variables, not here.
ENV JWT_SECRET=TheChurchManager@2025
ENV JWT_EXPIRY=30d
ENV MONGO_URI=mongodb://localhost:27017
ENV MONGO_DATABASE_NAME=TheChurchManager

EXPOSE 8080

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
