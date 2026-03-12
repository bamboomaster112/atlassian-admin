"""Audit permissions across Jira and Confluence (batched)."""

import asyncio
import logging
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import PermissionAuditEntry

logger = logging.getLogger(__name__)


async def audit_jira_global_permissions() -> list[PermissionAuditEntry]:
    """Check who holds global Jira permissions."""
    data = await atlassian_client.jira_get("/permissions")
    return [
        PermissionAuditEntry(
            entity_type="global",
            entity_name=perm_key,
            product="jira",
            scope="global",
            permissions=[perm_info.get("name", perm_key)],
        )
        for perm_key, perm_info in data.get("permissions", {}).items()
    ]


async def audit_jira_project_permissions(project_key: str) -> list[PermissionAuditEntry]:
    """Audit permissions for a specific Jira project."""
    try:
        scheme = await atlassian_client.jira_get(
            f"/project/{project_key}/permissionscheme"
        )
    except Exception as e:
        logger.warning(f"Cannot fetch permission scheme for project {project_key}: {e}")
        return []

    entries = []
    for grant in scheme.get("permissions", []):
        holder = grant.get("holder", {})
        entries.append(
            PermissionAuditEntry(
                entity_type=holder.get("type", "unknown"),
                entity_name=holder.get("parameter", holder.get("type", "")),
                product="jira",
                scope="project",
                scope_key=project_key,
                permissions=[grant.get("permission", "")],
            )
        )
    return entries


async def audit_confluence_space_permissions(space_key: str) -> list[PermissionAuditEntry]:
    """Audit permissions for a Confluence space."""
    try:
        space = await atlassian_client.confluence_get(
            f"/space/{space_key}", params={"expand": "permissions"},
        )
    except Exception as e:
        logger.warning(f"Cannot fetch permissions for space {space_key}: {e}")
        return []

    entries = []
    for perm in space.get("permissions", []):
        subjects = perm.get("subjects", {})
        operation = perm.get("operation", {}).get("operation", "")
        for subject_type in ("user", "group"):
            for subj in subjects.get(subject_type, {}).get("results", []):
                name = subj.get("displayName", subj.get("name", "unknown"))
                entries.append(
                    PermissionAuditEntry(
                        entity_type=subject_type,
                        entity_name=name,
                        product="confluence",
                        scope="space",
                        scope_key=space_key,
                        permissions=[operation],
                    )
                )
    return entries


async def get_full_permissions_audit() -> dict:
    """Run a full permissions audit across products (batched)."""
    # Fetch global + project/space lists concurrently
    jira_global_task = audit_jira_global_permissions()
    projects_task = atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/project/search", max_results=20
    )
    spaces_task = atlassian_client.get_paginated(
        f"{settings.confluence_rest_url}/space", max_results=20
    )

    jira_global, projects, spaces = await asyncio.gather(
        jira_global_task, projects_task, spaces_task
    )

    # Batch project permission audits
    proj_batch = await atlassian_client.batch(
        projects,
        lambda p: audit_jira_project_permissions(p["key"]),
        concurrency=5,
    )
    jira_project_perms = []
    for _, perms in proj_batch:
        if perms:
            jira_project_perms.extend(perms)

    # Batch space permission audits
    space_batch = await atlassian_client.batch(
        spaces,
        lambda s: audit_confluence_space_permissions(s["key"]),
        concurrency=5,
    )
    confluence_perms = []
    for _, perms in space_batch:
        if perms:
            confluence_perms.extend(perms)

    return {
        "jira_global_permissions": [e.model_dump() for e in jira_global],
        "jira_project_permissions": [e.model_dump() for e in jira_project_perms],
        "confluence_space_permissions": [e.model_dump() for e in confluence_perms],
        "total_entries": len(jira_global) + len(jira_project_perms) + len(confluence_perms),
    }
