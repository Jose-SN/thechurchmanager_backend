import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import os

from app.db.mongodb import connect_db
from app.db.postgresql import get_connection
from app.api.routers import router  # Assuming routers/__init__.py
from app.api.websocket import websocket_endpoint

app = FastAPI(title="The Church Manager")

# CORS (allow frontend origin)
# Note: When allow_credentials=True, you cannot use "*" as a wildcard
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://thechurchmanager.com", 
        "https://thechurchmanager.com", 
        "http://www.thechurchmanager.com", 
        "https://www.thechurchmanager.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
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
app.mount("/public", StaticFiles(directory="public"), name="public")



@app.on_event("startup")
async def startup_event():
    app.state.db = await get_connection()

app.include_router(router)

if __name__ == "__main__":
    async def startup():
        app.state.db = await get_connection()
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
    asyncio.run(startup())