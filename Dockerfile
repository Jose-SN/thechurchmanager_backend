# Use a lightweight Python image
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Non-secret defaults only. Set DATABASE_URL, JWT_SECRET, etc. in Railway Variables.
ENV MONGO_URI=mongodb://127.0.0.1:27017
ENV MONGO_DATABASE_NAME=TheChurchManager
ENV DATABASE_URL=postgresql://postgres.aatufidepwkgcoofspmp:PetaxAI091224@aws-1-eu-north-1.pooler.supabase.com:5432/postgres

EXPOSE 8080

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
