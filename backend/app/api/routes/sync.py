"""Data sync endpoints — trigger syncs and view history."""

from fastapi import APIRouter
from ...core.database import get_supabase
from ...services.sync import run_full_sync, sync_dashboard_snapshot

router = APIRouter(prefix="/sync", tags=["Sync"])


@router.post("/run")
async def trigger_full_sync():
    """Manually trigger a full data sync from Atlassian to Supabase."""
    results = await run_full_sync()
    return {"status": "completed", "results": results}


@router.post("/snapshot")
async def trigger_snapshot():
    """Take a dashboard snapshot only."""
    row = await sync_dashboard_snapshot()
    return {"status": "completed", "snapshot": row}


@router.get("/history")
async def sync_history(limit: int = 50):
    """View recent sync history."""
    sb = get_supabase()
    result = sb.table("sync_history") \
        .select("*") \
        .order("synced_at", desc=True) \
        .limit(limit) \
        .execute()
    return result.data


@router.get("/history/{category}")
async def sync_history_by_category(category: str, limit: int = 20):
    """View sync history for a specific category."""
    sb = get_supabase()
    result = sb.table("sync_history") \
        .select("*") \
        .eq("category", category) \
        .order("synced_at", desc=True) \
        .limit(limit) \
        .execute()
    return result.data
