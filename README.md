# thechurchmanager_backend

## Setup

```bash
pip install -r requirements.txt
```

🛠 Example setup commands
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

To run:

```bash
uvicorn main:app --reload
```

Build Docker Image

```bash
docker build -t fastapi-app .
```

Run Docker locally

```bash
docker run -p 8080:8080 fastapi-app
```

# 1. Create a repo in ECR (Amazon Elastic Container Registry)

    Create Registry - fastapi-app

# 2. Authenticate Docker:

```bash
aws login

aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 545009850195.dkr.ecr.eu-west-2.amazonaws.com
```

# 3. Tag your image:

```bash
docker tag fastapi-app:latest 545009850195.dkr.ecr.eu-west-2.amazonaws.com/fastapi-app:latest
```

# 4. Push to ECR:

```bash
docker push 545009850195.dkr.ecr.eu-west-2.amazonaws.com/fastapi-app:latest
```


1. Go to AWS Console → App Runner.
2. Click on "Create Service".
3. Select "Container registry".
4. Choose "ECR" and select your image.
5. Set the port to 8080.
6. Set environment variables as needed.
7. Click "Deploy".


Usage

1. Make it executable:

    chmod +x deploy.py

2. Deploy and push to ECR without running locally:

    ./deploy.py

3. Deploy and run locally:

    ./deploy.py --run-local
