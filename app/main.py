from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import os

from app.dbhandler import connect_db
from routers import router  # Assuming routers/__init__.py
from app.websocket import websocket_endpoint

app = FastAPI()

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return response

# CORS (if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (equivalent to express.static)
app.mount("/public", StaticFiles(directory="public"), name="public")

# Routers
app.include_router(router)

# WebSocket endpoint
app.add_api_websocket_route("/ws", websocket_endpoint)

# Run server + DB connection
if __name__ == "__main__":
    import asyncio

    async def startup():
        await connect_db()
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

    asyncio.run(startup())
