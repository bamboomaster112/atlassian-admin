"""Audit permissions across Jira and Confluence."""

from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import PermissionAuditEntry


async def audit_jira_global_permissions() -> list[PermissionAuditEntry]:
    """Check who holds global Jira permissions."""
    data = await atlassian_client.jira_get("/permissions")
    entries = []
    for perm_key, perm_info in data.get("permissions", {}).items():
        entries.append(
            PermissionAuditEntry(
                entity_type="global",
                entity_name=perm_key,
                product="jira",
                scope="global",
                permissions=[perm_info.get("name", perm_key)],
            )
        )
    return entries


async def audit_jira_project_permissions(project_key: str) -> list[PermissionAuditEntry]:
    """Audit permissions for a specific Jira project."""
    # Get the permission scheme for the project
    try:
        scheme = await atlassian_client.jira_get(
            f"/project/{project_key}/permissionscheme"
        )
    except Exception:
        return []

    entries = []
    for grant in scheme.get("permissions", []):
        holder = grant.get("holder", {})
        entity_type = holder.get("type", "unknown")
        entity_name = holder.get("parameter", holder.get("type", ""))

        entries.append(
            PermissionAuditEntry(
                entity_type=entity_type,
                entity_name=entity_name,
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
            f"/space/{space_key}",
            params={"expand": "permissions"},
        )
    except Exception:
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
    """Run a full permissions audit across products."""
    # Jira global
    jira_global = await audit_jira_global_permissions()

    # Jira per-project (sample first 20 projects)
    projects = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/project/search", max_results=20
    )
    jira_project_perms = []
    for p in projects:
        perms = await audit_jira_project_permissions(p["key"])
        jira_project_perms.extend(perms)

    # Confluence per-space (sample first 20 spaces)
    spaces = await atlassian_client.get_paginated(
        f"{settings.confluence_rest_url}/space", max_results=20
    )
    confluence_perms = []
    for s in spaces:
        perms = await audit_confluence_space_permissions(s["key"])
        confluence_perms.extend(perms)

    return {
        "jira_global_permissions": [e.model_dump() for e in jira_global],
        "jira_project_permissions": [e.model_dump() for e in jira_project_perms],
        "confluence_space_permissions": [e.model_dump() for e in confluence_perms],
        "total_entries": len(jira_global) + len(jira_project_perms) + len(confluence_perms),
    }
