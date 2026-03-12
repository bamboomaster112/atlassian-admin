"""Jira tracking endpoints."""

from fastapi import APIRouter, Query

from ...services.jira.user_tracking import (
    get_all_jira_users,
    get_user_activity,
    get_inactive_users,
    get_user_activity_summary,
)
from ...services.jira.custom_fields import (
    get_all_custom_fields,
    get_custom_field_usage,
    get_unused_custom_fields,
    get_custom_field_cleanup_recommendations,
)
from ...services.jira.workflows import get_all_schemes_summary
from ...services.jira.projects import get_all_projects, get_project_detail
from ...services.jira.configuration import (
    get_all_issue_types,
    get_all_statuses,
    get_all_priorities,
    get_all_resolutions,
    get_all_screens,
    get_all_screen_schemes,
    get_all_issue_type_screen_schemes,
    get_all_field_configurations,
    get_all_field_config_schemes,
    get_all_project_categories,
    get_all_project_roles,
    get_full_configuration,
)
from ...services.jira.groups import (
    get_all_groups,
    get_all_groups_with_members,
    get_application_roles,
)
from ...services.jira.filters_dashboards import (
    get_all_filters,
    get_all_dashboards,
    get_filters_dashboards_summary,
)
from ...services.jira.audit import get_audit_records, get_instance_info

router = APIRouter(prefix="/jira", tags=["Jira"])


# ── Users ─────────────────────────────────────────────

@router.get("/users")
async def list_users(active_only: bool = False):
    return await get_all_jira_users(active_only=active_only)


@router.get("/users/activity-summary")
async def user_activity_summary(days: int = Query(30, ge=1, le=365)):
    return await get_user_activity_summary(days=days)


@router.get("/users/{account_id}/activity")
async def user_activity(account_id: str, days: int = Query(30, ge=1, le=365)):
    return await get_user_activity(account_id, days=days)


@router.get("/users/inactive")
async def inactive_users(days: int = Query(90, ge=1, le=365)):
    return await get_inactive_users(days=days)


# ── Custom Fields ─────────────────────────────────────

@router.get("/custom-fields")
async def list_custom_fields():
    return await get_all_custom_fields()


@router.get("/custom-fields/unused")
async def unused_custom_fields():
    return await get_unused_custom_fields()


@router.get("/custom-fields/{field_id}/usage")
async def custom_field_usage(field_id: str):
    return await get_custom_field_usage(field_id)


@router.get("/custom-fields/cleanup-recommendations")
async def custom_field_recommendations():
    return await get_custom_field_cleanup_recommendations()


# ── Workflows & Schemes ──────────────────────────────

@router.get("/schemes")
async def all_schemes():
    return await get_all_schemes_summary()


# ── Projects ──────────────────────────────────────────

@router.get("/projects")
async def list_projects():
    return await get_all_projects()


@router.get("/projects/{project_key}")
async def project_detail(project_key: str):
    return await get_project_detail(project_key)


# ── Configuration ────────────────────────────────────

@router.get("/configuration")
async def full_configuration():
    """All Jira configuration entities in one call."""
    return await get_full_configuration()


@router.get("/issue-types")
async def list_issue_types():
    return await get_all_issue_types()


@router.get("/statuses")
async def list_statuses():
    return await get_all_statuses()


@router.get("/priorities")
async def list_priorities():
    return await get_all_priorities()


@router.get("/resolutions")
async def list_resolutions():
    return await get_all_resolutions()


@router.get("/screens")
async def list_screens():
    return await get_all_screens()


@router.get("/screen-schemes")
async def list_screen_schemes():
    return await get_all_screen_schemes()


@router.get("/issue-type-screen-schemes")
async def list_issue_type_screen_schemes():
    return await get_all_issue_type_screen_schemes()


@router.get("/field-configurations")
async def list_field_configurations():
    return await get_all_field_configurations()


@router.get("/field-config-schemes")
async def list_field_config_schemes():
    return await get_all_field_config_schemes()


@router.get("/project-categories")
async def list_project_categories():
    return await get_all_project_categories()


@router.get("/project-roles")
async def list_project_roles():
    return await get_all_project_roles()


# ── Groups ───────────────────────────────────────────

@router.get("/groups")
async def list_groups():
    return await get_all_groups()


@router.get("/groups/with-members")
async def list_groups_with_members():
    return await get_all_groups_with_members()


@router.get("/application-roles")
async def list_application_roles():
    return await get_application_roles()


# ── Filters & Dashboards ────────────────────────────

@router.get("/filters")
async def list_filters():
    return await get_all_filters()


@router.get("/dashboards")
async def list_dashboards():
    return await get_all_dashboards()


@router.get("/filters-dashboards")
async def filters_dashboards():
    return await get_filters_dashboards_summary()


# ── Audit & Instance ────────────────────────────────

@router.get("/audit-log")
async def audit_log(limit: int = Query(200, ge=1, le=1000)):
    return await get_audit_records(limit=limit)


@router.get("/instance-info")
async def instance_info():
    return await get_instance_info()
