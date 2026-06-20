import asyncio
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import os

from app.db.mongodb import connect_db
from app.db.postgresql import get_connection
from app.db.session import init_sqlalchemy, close_sqlalchemy
from app.api.routers import router  # Assuming routers/__init__.py
from app.api.websocket import websocket_endpoint
from app.utils.mail import test_smtp_connection

app = FastAPI(title="The Church Manager")

# CORS — explicit dev origins (wildcard + credentials is invalid in browsers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "https://thechurchmanager.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Organization-Id"],
    expose_headers=["*"],
)

# Security headers middleware (placed after CORS to avoid conflicts)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Only set these headers if not already set by CORS middleware
    if "Cross-Origin-Opener-Policy" not in response.headers:
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    # Commented out as it can interfere with CORS
    # response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return response

# Static files (equivalent to express.static)
PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
os.makedirs(PUBLIC_DIR, exist_ok=True)
app.mount("/public", StaticFiles(directory=PUBLIC_DIR), name="public")



@app.on_event("startup")
async def startup_event():
    app.state.db = await get_connection()
    await init_sqlalchemy()
    # Test Gmail SMTP connection at startup (non-blocking - app will start even if this fails)
    try:
        test_smtp_connection()
    except Exception as e:
        logging.warning(f"⚠️ Gmail SMTP test failed, but continuing startup: {e}")
        print(f"⚠️ Gmail SMTP test failed, but continuing startup: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    await close_sqlalchemy()

app.include_router(router)

if __name__ == "__main__":
    async def startup():
        app.state.db = await get_connection()
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
    asyncio.run(startup())