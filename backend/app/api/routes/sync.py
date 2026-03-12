"""Data sync endpoints — trigger syncs and view history."""

import asyncio
import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from ...core.database import get_supabase
from ...services.sync import run_full_sync, sync_dashboard_snapshot

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sync", tags=["Sync"])

# Simple in-memory flag to prevent concurrent syncs
_sync_running = False


async def _run_sync_background():
    """Background task wrapper for full sync."""
    global _sync_running
    try:
        await run_full_sync()
    except Exception as e:
        logger.error(f"Background sync failed: {e}")
    finally:
        _sync_running = False


@router.post("/run")
async def trigger_full_sync_endpoint(background_tasks: BackgroundTasks, background: bool = Query(False)):
    """Trigger a full data sync. Set ?background=true to run async."""
    global _sync_running
    if _sync_running:
        raise HTTPException(status_code=409, detail="A sync is already in progress")

    if background:
        _sync_running = True
        background_tasks.add_task(_run_sync_background)
        return {"status": "started", "message": "Sync running in background. Check /api/sync/history for progress."}

    _sync_running = True
    try:
        results = await run_full_sync()
        return {"status": "completed", "results": results}
    finally:
        _sync_running = False


@router.get("/status")
async def sync_status():
    """Check if a sync is currently running."""
    return {"running": _sync_running}


@router.post("/snapshot")
async def trigger_snapshot():
    """Take a dashboard snapshot only."""
    try:
        row = await sync_dashboard_snapshot()
        return {"status": "completed", "snapshot": row}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def sync_history(limit: int = Query(50, ge=1, le=500)):
    """View recent sync history."""
    try:
        sb = get_supabase()
        result = sb.table("sync_history") \
            .select("*") \
            .order("synced_at", desc=True) \
            .limit(limit) \
            .execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sync history: {e}")


@router.get("/history/{category}")
async def sync_history_by_category(category: str, limit: int = Query(20, ge=1, le=200)):
    """View sync history for a specific category."""
    try:
        sb = get_supabase()
        result = sb.table("sync_history") \
            .select("*") \
            .eq("category", category) \
            .order("synced_at", desc=True) \
            .limit(limit) \
            .execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sync history: {e}")
