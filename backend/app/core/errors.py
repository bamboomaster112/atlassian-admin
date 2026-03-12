"""Global error handlers for the FastAPI application."""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from .atlassian_client import AtlassianAPIError

logger = logging.getLogger(__name__)


async def atlassian_api_error_handler(request: Request, exc: AtlassianAPIError):
    """Convert Atlassian API errors into structured HTTP responses."""
    status = 502 if exc.status_code and exc.status_code >= 500 else 503
    if exc.status_code == 401:
        status = 401
    elif exc.status_code == 403:
        status = 403
    elif exc.status_code == 404:
        status = 404

    logger.error(f"Atlassian API error: {exc} (url={exc.url})")
    return JSONResponse(
        status_code=status,
        content={
            "error": "atlassian_api_error",
            "message": str(exc),
            "upstream_status": exc.status_code,
        },
    )


async def generic_error_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions."""
    logger.exception(f"Unhandled error on {request.method} {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred. Check server logs.",
        },
    )
