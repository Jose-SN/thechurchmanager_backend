# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (optional but recommended)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (better caching)
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

ENV PORT=5000
ENV JWT_SECRET=TheChurchManager@2025
ENV JWT_EXPIRY=30d
ENV FILEUPLOADLIMIT=5
ENV MONGO_URI=mongodb://localhost:27017
ENV MONGO_DATABASE_NAME=TheChurchManager
ENV MONGO_PROD_URI="mongodb+srv://petaxailtd:Petaxailtd%40123@betrack.dtmqf.mongodb.net/?retryWrites=true&w=majority&appName=TheChurchManager"
ENV GMAIL_USERNAME=petaxailtd@gmail.com
ENV GMAIL_PASS="jbbu ruci hsvl gkst"
ENV EC2_PUBLIC_IP=18.175.122.53
ENV ENABLED_PROTOCOL=http
ENV AWS_ACCESS_KEY_ID=AKIAX5ZI6K5JRTAF2DUO
ENV AWS_SECRET_ACCESS_KEY=o0H2XqQEPRsEi4DVANKzP4DU0oN4JHxtKdCoPXk4
ENV S3_BUCKET_NAME=betrack
ENV AWS_REGION=eu-west-2

# Expose port (App Runner expects your app to listen on 8080)
EXPOSE 8080

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
