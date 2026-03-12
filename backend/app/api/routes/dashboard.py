"""Dashboard overview endpoints."""

import asyncio
from fastapi import APIRouter, Query

from ...core.database import get_supabase
from ...services.jira.projects import get_all_projects
from ...services.jira.custom_fields import get_all_custom_fields, get_unused_custom_fields
from ...services.jira.user_tracking import get_all_jira_users
from ...services.jira.workflows import get_all_workflows, get_all_schemes_summary
from ...services.jira.groups import get_all_groups
from ...services.jira.filters_dashboards import get_all_filters, get_all_dashboards
from ...services.confluence.spaces import get_all_spaces
from ...services.jsm.service_desks import get_all_service_desks
from ...services.governance.cleanup import get_all_recommendations
from ...models.schemas import AdminDashboard

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", response_model=AdminDashboard)
async def get_dashboard():
    """Top-level admin dashboard with key metrics (live from Atlassian)."""
    (
        projects, spaces, desks, users, custom_fields, unused_fields,
        recs, workflows, groups, filters, dashboards
    ) = await asyncio.gather(
        get_all_projects(),
        get_all_spaces(),
        get_all_service_desks(),
        get_all_jira_users(),
        get_all_custom_fields(),
        get_unused_custom_fields(),
        get_all_recommendations(),
        get_all_workflows(),
        get_all_groups(),
        get_all_filters(),
        get_all_dashboards(),
    )

    schemes_summary = await get_all_schemes_summary()
    total_schemes = sum(
        v["count"] for v in schemes_summary.values()
        if isinstance(v, dict) and "count" in v
    )

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
        total_workflows=len(workflows),
        total_schemes=total_schemes,
        total_groups=len(groups),
        total_filters=len(filters),
        total_dashboards_jira=len(dashboards),
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
