"""
Main FastAPI application with performance and security optimizations.
"""

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse

from app.admin import setup_admin
from app.api.v1.router import api_router
from app.auth.users import auth_backend, fastapi_users
from app.core.config import settings
from app.core.middleware import SecurityHeadersMiddleware, TimingMiddleware
from app.core.redis import close_redis, get_redis
from app.schemas.user import UserCreate, UserRead, UserUpdate

if not os.environ.get("PYTEST_CURRENT_TEST"):
    try:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    from app.core.websocket import get_manager

    await get_redis()
    await get_manager()
    yield
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-time chat application backend API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": False,
        "clientId": "swagger",
        "clientSecret": "",
    },
    default_response_class=ORJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(TimingMiddleware)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

setup_admin(app)


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({"status": "healthy", "version": settings.APP_VERSION})


@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint."""
    return JSONResponse(
        {
            "message": "Welcome to Realtime Chat API",
            "version": settings.APP_VERSION,
            "docs": "/docs",
        }
    )
