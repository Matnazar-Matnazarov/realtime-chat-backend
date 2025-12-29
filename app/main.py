"""
Main FastAPI application.
"""

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.admin import setup_admin
from app.api.v1.router import api_router
from app.auth.users import auth_backend, fastapi_users
from app.core.config import settings
from app.core.redis import close_redis, get_redis
from app.schemas.user import UserCreate, UserRead, UserUpdate

# Configure uvloop only if not running in pytest
# Pytest uses standard asyncio event loop to avoid conflicts
if not os.environ.get("PYTEST_CURRENT_TEST"):
    try:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass  # uvloop not available, use default event loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    from app.core.websocket import get_manager

    await get_redis()  # Initialize Redis connection
    await get_manager()  # Initialize WebSocket manager
    yield
    # Shutdown
    await close_redis()


# Create FastAPI app
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
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Include fastapi-users auth routes
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

# OAuth routes (if configured)
# Note: OAuth setup requires additional configuration
# Uncomment and configure when OAuth credentials are available
# if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
#     from fastapi_users.authentication import CookieTransport
#     from app.auth.oauth import get_google_oauth_router
#     from app.auth.users import get_user_manager
#
#     cookie_transport = CookieTransport(cookie_max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
#     async def get_user_manager_dep():
#         async for manager in get_user_manager():
#             yield manager
#
#     app.include_router(
#         get_google_oauth_router(
#             get_user_manager_dep,
#             settings.SECRET_KEY,
#             cookie_transport,
#         ),
#         prefix="/auth/google",
#         tags=["auth"],
#     )

# Admin panel
setup_admin(app)


# Health check
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
