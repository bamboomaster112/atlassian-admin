"""Admin governance endpoints — licenses, permissions, cleanup."""

from fastapi import APIRouter, Query

from ...services.governance.license_tracking import get_license_summary
from ...services.governance.permissions_audit import (
    get_full_permissions_audit,
    audit_jira_project_permissions,
    audit_confluence_space_permissions,
)
from ...services.governance.cleanup import get_all_recommendations

router = APIRouter(prefix="/governance", tags=["Governance"])


# ── Licenses ──────────────────────────────────────────

@router.get("/licenses")
async def license_summary():
    return await get_license_summary()


# ── Permissions ───────────────────────────────────────

@router.get("/permissions/audit")
async def full_permissions_audit():
    return await get_full_permissions_audit()


@router.get("/permissions/jira/{project_key}")
async def jira_project_permissions(project_key: str):
    return await audit_jira_project_permissions(project_key)


@router.get("/permissions/confluence/{space_key}")
async def confluence_space_permissions(space_key: str):
    return await audit_confluence_space_permissions(space_key)


# ── Cleanup ───────────────────────────────────────────

@router.get("/cleanup")
async def cleanup_recommendations():
    return await get_all_recommendations()
