"""
Custom middleware for performance monitoring and security.
"""

import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to add request timing with high precision."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add timing header to response with microsecond precision."""
        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            process_time = time.perf_counter() - start_time
            raise
        else:
            process_time = time.perf_counter() - start_time
            response.headers["X-Process-Time"] = f"{process_time:.6f}"
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        if not request.url.path.startswith("/docs") and not request.url.path.startswith("/redoc"):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
