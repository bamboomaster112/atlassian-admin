"""Atlassian Admin Tracker — FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.database import init_db
from .core.atlassian_client import AtlassianAPIError
from .core.errors import atlassian_api_error_handler, generic_error_handler
from .api.routes import dashboard, jira, confluence, jsm, governance, sync

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Administration governance & usage tracking for Jira, Confluence, and Jira Service Management",
    lifespan=lifespan,
)

# Error handlers
app.add_exception_handler(AtlassianAPIError, atlassian_api_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(dashboard.router, prefix="/api")
app.include_router(jira.router, prefix="/api")
app.include_router(confluence.router, prefix="/api")
app.include_router(jsm.router, prefix="/api")
app.include_router(governance.router, prefix="/api")
app.include_router(sync.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
