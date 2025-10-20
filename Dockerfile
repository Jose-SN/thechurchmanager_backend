# Use official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only dependency files first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose App Runner default port
ENV PORT=8080
EXPOSE 8080

# Run FastAPI with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
