#!/usr/bin/env python3
import subprocess
import argparse
import sys

# ------------------------
# Configuration
# ------------------------
APP_NAME = "fastapi-app"
PORT = 8080
AWS_REGION = "eu-west-2"
ECR_URI = f"545009850195.dkr.ecr.{AWS_REGION}.amazonaws.com/{APP_NAME}:latest"

# ------------------------
# Helper function to run shell commands
# ------------------------
def run_cmd(command, verbose=True):
    if verbose:
        print(f"> {command}")
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

# ------------------------
# Main deployment function
# ------------------------
def deploy(run_local=False):
    # 1. AWS ECR login
    print("Logging in to AWS ECR...")
    run_cmd(f"aws ecr get-login-password --region {AWS_REGION} | docker login --username AWS --password-stdin 545009850195.dkr.ecr.{AWS_REGION}.amazonaws.com")

    # 2. Build Docker image
    print("Building Docker image...")
    run_cmd(f"docker build -t {APP_NAME} .")

    # 3. Run locally (optional)
    if run_local:
        print(f"Running Docker container locally on port {PORT}...")
        run_cmd(f"docker run -d -p {PORT}:{PORT} {APP_NAME}")

    # 4. Tag Docker image for ECR
    print("Tagging Docker image for ECR...")
    run_cmd(f"docker tag {APP_NAME}:latest {ECR_URI}")

    # 5. Push Docker image to ECR
    print("Pushing Docker image to ECR...")
    run_cmd(f"docker push {ECR_URI}")

    print("\n✅ Deployment complete!")

# ------------------------
# Command-line interface
# ------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy FastAPI Docker app to AWS ECR")
    parser.add_argument("--run-local", action="store_true", help="Run container locally after building")
    args = parser.parse_args()

    deploy(run_local=args.run_local)
