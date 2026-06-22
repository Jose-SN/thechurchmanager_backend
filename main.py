import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from app.db.postgresql import close_postgresql, get_connection
from app.db.session import init_sqlalchemy, close_sqlalchemy
from app.api.routers import router
from app.utils.mail import test_smtp_connection
from app.core.config import settings

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = None

    async def init_databases():
        try:
            if not settings.is_postgresql_configured():
                logging.error(
                    "DATABASE_URL is not set. Add it in Railway Variables."
                )
                return
            app.state.db = await get_connection(retries=3, delay_seconds=2.0)
            await init_sqlalchemy()
            logging.info("PostgreSQL pool ready")
        except Exception as exc:
            logging.error("Database initialization failed: %s", exc)
            app.state.db = None

    app.state.db_init_task = asyncio.create_task(init_databases())

    async def test_smtp_later():
        try:
            await asyncio.to_thread(test_smtp_connection)
        except Exception as exc:
            logging.warning("Gmail SMTP test failed: %s", exc)

    asyncio.create_task(test_smtp_later())

    yield

    task = getattr(app.state, "db_init_task", None)
    if task and not task.done():
        task.cancel()
    await close_sqlalchemy()
    await close_postgresql()


app = FastAPI(title="The Church Manager", lifespan=lifespan)


@app.get("/health", tags=["Health"], include_in_schema=True)
async def health_check():
    """Railway liveness probe — must respond before DB init completes."""
    db_ready = getattr(app.state, "db", None) is not None
    return {
        "status": "ok",
        "db": "connected" if db_ready else "connecting",
        "time": datetime.now(timezone.utc).isoformat(),
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "https://thechurchmanager.com",
        "https://www.thechurchmanager.com",
        "https://thechurchmanagerbackend-production.up.railway.app",
        "https://iam-production-e81f.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Organization-Id"],
    expose_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    if "Cross-Origin-Opener-Policy" not in response.headers:
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    return response


PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
os.makedirs(PUBLIC_DIR, exist_ok=True)
app.mount("/public", StaticFiles(directory=PUBLIC_DIR), name="public")

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
