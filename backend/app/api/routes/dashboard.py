"""Dashboard overview endpoints."""

from fastapi import APIRouter, Query

from ...core.database import get_supabase
from ...services.jira.projects import get_all_projects
from ...services.jira.custom_fields import get_all_custom_fields, get_unused_custom_fields
from ...services.jira.user_tracking import get_all_jira_users
from ...services.confluence.spaces import get_all_spaces
from ...services.jsm.service_desks import get_all_service_desks
from ...services.governance.cleanup import get_all_recommendations
from ...models.schemas import AdminDashboard

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", response_model=AdminDashboard)
async def get_dashboard():
    """Top-level admin dashboard with key metrics (live from Atlassian)."""
    projects = await get_all_projects()
    spaces = await get_all_spaces()
    desks = await get_all_service_desks()
    users = await get_all_jira_users()
    custom_fields = await get_all_custom_fields()
    unused_fields = await get_unused_custom_fields()
    recs = await get_all_recommendations()

    active_users = sum(1 for u in users if u.active)

    return AdminDashboard(
        jira_projects=len(projects),
        confluence_spaces=len(spaces),
        jsm_service_desks=len(desks),
        total_users=len(users),
        active_users=active_users,
        inactive_users=len(users) - active_users,
        custom_fields_total=len(custom_fields),
        custom_fields_unused=len(unused_fields),
        cleanup_recommendations=recs["total_recommendations"],
    )


@router.get("/cached")
async def get_dashboard_cached():
    """Return the most recent dashboard snapshot from Supabase (fast, no Atlassian calls)."""
    sb = get_supabase()
    result = sb.table("dashboard_snapshots") \
        .select("*") \
        .order("synced_at", desc=True) \
        .limit(1) \
        .execute()
    if result.data:
        return result.data[0]
    return {"message": "No snapshots yet. Trigger a sync first via POST /api/sync/run"}


@router.get("/trends")
async def get_dashboard_trends(limit: int = Query(30, ge=1, le=365)):
    """Return historical dashboard snapshots for trend charts."""
    sb = get_supabase()
    result = sb.table("dashboard_snapshots") \
        .select("*") \
        .order("synced_at", desc=True) \
        .limit(limit) \
        .execute()
    return result.data
