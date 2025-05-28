from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

def setup_security(app: FastAPI):
    # CORS Middleware (allow all origins by default, customize as needed)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # or list your allowed origins here
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trust proxy setting is automatic in many ASGI servers,
    # but if behind proxies, configure them accordingly

    # HTTPS redirect only in production and if request is HTTP
    if os.getenv("NODE_ENV") == "production":
        app.add_middleware(HTTPSRedirectMiddleware)

    # Custom middleware to replicate the HTTP->HTTPS redirect logic more explicitly
    # (if you want to handle manually instead of HTTPSRedirectMiddleware)

    @app.middleware("http")
    async def redirect_http_to_https(request: Request, call_next):
        if os.getenv("NODE_ENV") == "production":
            if request.url.scheme == "http":
                url = request.url.replace(scheme="https")
                return RedirectResponse(url)
        response = await call_next(request)
        return response

    # Helmet equivalent - security headers can be set using middleware:
    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        # Disable contentSecurityPolicy & crossOriginOpenerPolicy as in your Node code
        # Set some common helmet-like headers:
        response.headers["X-DNS-Prefetch-Control"] = "off"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Download-Options"] = "noopen"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        # crossOriginOpenerPolicy is off per your code, so don't set it
        return response

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Apply rate limit globally - 100 requests per 30 seconds per IP
    @app.middleware("http")
    @limiter.limit("100/30seconds")
    async def rate_limit_middleware(request: Request, call_next):
        return await call_next(request)
