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
