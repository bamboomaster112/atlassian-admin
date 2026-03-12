"""Confluence tracking endpoints."""

from fastapi import APIRouter, Query

from ...services.confluence.spaces import (
    get_all_spaces,
    get_space_detail,
    get_space_growth_summary,
)
from ...services.confluence.content import (
    get_recently_updated_content,
    get_stale_content,
    get_top_contributors,
    get_label_usage,
)

router = APIRouter(prefix="/confluence", tags=["Confluence"])


# ── Spaces ────────────────────────────────────────────

@router.get("/spaces")
async def list_spaces():
    return await get_all_spaces()


@router.get("/spaces/growth-summary")
async def space_growth_summary():
    return await get_space_growth_summary()


@router.get("/spaces/{space_key}")
async def space_detail(space_key: str):
    return await get_space_detail(space_key)


# ── Content ───────────────────────────────────────────

@router.get("/content/recent")
async def recent_content(days: int = Query(30, ge=1, le=365), limit: int = Query(50, ge=1, le=200)):
    return await get_recently_updated_content(days=days, limit=limit)


@router.get("/content/stale")
async def stale_content(days: int = Query(365, ge=30), limit: int = Query(100, ge=1, le=500)):
    return await get_stale_content(days=days, limit=limit)


@router.get("/content/top-contributors")
async def top_contributors(days: int = Query(30, ge=1, le=365), limit: int = Query(20, ge=1, le=100)):
    return await get_top_contributors(days=days, limit=limit)


@router.get("/content/labels")
async def label_usage():
    return await get_label_usage()
