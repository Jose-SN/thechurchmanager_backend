import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import os

from app.db.mongodb import connect_db
from app.api.routers import router  # Assuming routers/__init__.py
from app.api.websocket import websocket_endpoint

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



app = FastAPI(title="The Church Manager")

@app.on_event("startup")
async def startup_event():
    app.state.db = await connect_db()

app.include_router(router)

if __name__ == "__main__":
    async def startup():
        app.state.db = await connect_db()
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
    asyncio.run(startup())