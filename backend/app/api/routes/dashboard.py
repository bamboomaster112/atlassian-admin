"""Dashboard overview endpoints."""

from fastapi import APIRouter

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
    """Top-level admin dashboard with key metrics."""
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
