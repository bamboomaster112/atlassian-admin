"""Jira configuration entities — issue types, statuses, priorities, resolutions,
screens, screen schemes, field configurations, project categories, project roles."""

import asyncio
import logging
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import (
    IssueType, JiraStatus, JiraPriority, JiraResolution,
    JiraScreen, JiraScreenScheme, IssueTypeScreenScheme,
    FieldConfiguration, FieldConfigScheme, ProjectCategory,
    ProjectRole, ProjectRoleActor,
)

logger = logging.getLogger(__name__)


# ── Issue Types ──────────────────────────────────────

async def get_all_issue_types() -> list[IssueType]:
    data = await atlassian_client.jira_get("/issuetype")
    return [
        IssueType(
            issue_type_id=str(it.get("id", "")),
            name=it.get("name", ""),
            description=it.get("description"),
            icon_url=it.get("iconUrl"),
            subtask=it.get("subtask", False),
            hierarchy_level=it.get("hierarchyLevel", 0),
            scope=f"project:{it['scope']['project']['id']}" if it.get("scope", {}).get("project") else "global",
            avatar_id=str(it.get("avatarId", "")),
        )
        for it in data
    ]


# ── Statuses ─────────────────────────────────────────

async def get_all_statuses() -> list[JiraStatus]:
    data = await atlassian_client.jira_get("/status")
    return [
        JiraStatus(
            status_id=str(s.get("id", "")),
            name=s.get("name", ""),
            description=s.get("description"),
            status_category=s.get("statusCategory", {}).get("key", "undefined"),
            status_category_id=str(s.get("statusCategory", {}).get("id", "")),
            scope=f"project:{s['scope']['project']['id']}" if s.get("scope", {}).get("project") else "global",
        )
        for s in data
    ]


# ── Priorities ───────────────────────────────────────

async def get_all_priorities() -> list[JiraPriority]:
    data = await atlassian_client.jira_get("/priority")
    return [
        JiraPriority(
            priority_id=str(p.get("id", "")),
            name=p.get("name", ""),
            description=p.get("description"),
            icon_url=p.get("iconUrl"),
            status_color=p.get("statusColor"),
            is_default=p.get("isDefault", False),
        )
        for p in data
    ]


# ── Resolutions ──────────────────────────────────────

async def get_all_resolutions() -> list[JiraResolution]:
    data = await atlassian_client.jira_get("/resolution")
    return [
        JiraResolution(
            resolution_id=str(r.get("id", "")),
            name=r.get("name", ""),
            description=r.get("description"),
            is_default=r.get("isDefault", False),
        )
        for r in data
    ]


# ── Screens ──────────────────────────────────────────

async def get_all_screens() -> list[JiraScreen]:
    screens_raw = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/screens"
    )

    async def _fetch_tabs(screen):
        try:
            tabs_data = await atlassian_client.jira_get(f"/screens/{screen['id']}/tabs")
            tabs = []
            for tab in tabs_data:
                try:
                    fields_data = await atlassian_client.jira_get(
                        f"/screens/{screen['id']}/tabs/{tab['id']}/fields"
                    )
                    fields = [{"id": f.get("id"), "name": f.get("name")} for f in fields_data]
                except Exception:
                    fields = []
                tabs.append({"id": str(tab.get("id", "")), "name": tab.get("name", ""), "fields": fields})
            return tabs
        except Exception:
            return []

    batch_results = await atlassian_client.batch(screens_raw, _fetch_tabs, concurrency=5)

    return [
        JiraScreen(
            screen_id=str(s.get("id", "")),
            name=s.get("name", ""),
            description=s.get("description"),
            scope=f"project:{s['scope']['project']['id']}" if s.get("scope", {}).get("project") else "global",
            tab_count=len(tabs) if tabs else 0,
            tabs=tabs or [],
        )
        for s, tabs in batch_results
    ]


# ── Screen Schemes ───────────────────────────────────

async def get_all_screen_schemes() -> list[JiraScreenScheme]:
    data = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/screenscheme"
    )
    return [
        JiraScreenScheme(
            scheme_id=str(s.get("id", "")),
            name=s.get("name", ""),
            description=s.get("description"),
            screens={
                "default": str(s.get("screens", {}).get("default", "")),
                "create": str(s.get("screens", {}).get("create", "")),
                "edit": str(s.get("screens", {}).get("edit", "")),
                "view": str(s.get("screens", {}).get("view", "")),
            },
        )
        for s in data
    ]


# ── Issue Type Screen Schemes ────────────────────────

async def get_all_issue_type_screen_schemes() -> list[IssueTypeScreenScheme]:
    data = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/issuetypescreenscheme"
    )
    return [
        IssueTypeScreenScheme(
            scheme_id=str(s.get("id", "")),
            name=s.get("name", ""),
            description=s.get("description"),
        )
        for s in data
    ]


# ── Field Configurations ─────────────────────────────

async def get_all_field_configurations() -> list[FieldConfiguration]:
    data = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/fieldconfiguration"
    )
    return [
        FieldConfiguration(
            config_id=str(fc.get("id", "")),
            name=fc.get("name", ""),
            description=fc.get("description"),
            is_default=fc.get("isDefault", False),
        )
        for fc in data
    ]


# ── Field Configuration Schemes ──────────────────────

async def get_all_field_config_schemes() -> list[FieldConfigScheme]:
    data = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/fieldconfigurationscheme"
    )
    return [
        FieldConfigScheme(
            scheme_id=str(s.get("id", "")),
            name=s.get("name", ""),
            description=s.get("description"),
            is_default=s.get("isDefault", False),
        )
        for s in data
    ]


# ── Project Categories ───────────────────────────────

async def get_all_project_categories() -> list[ProjectCategory]:
    data = await atlassian_client.jira_get("/projectCategory")
    return [
        ProjectCategory(
            category_id=str(c.get("id", "")),
            name=c.get("name", ""),
            description=c.get("description"),
        )
        for c in data
    ]


# ── Project Roles ────────────────────────────────────

async def get_all_project_roles() -> list[ProjectRole]:
    data = await atlassian_client.jira_get("/role")
    return [
        ProjectRole(
            role_id=str(r.get("id", "")),
            name=r.get("name", ""),
            description=r.get("description"),
            is_admin=r.get("admin", False),
        )
        for r in data
    ]


async def get_project_role_actors(project_key: str) -> list[ProjectRoleActor]:
    """Fetch all role actors for a given project."""
    roles = await get_all_project_roles()
    actors = []

    async def _fetch_actors(role: ProjectRole):
        try:
            data = await atlassian_client.jira_get(
                f"/project/{project_key}/role/{role.role_id}"
            )
            result = []
            for actor in data.get("actors", []):
                result.append(ProjectRoleActor(
                    project_key=project_key,
                    role_id=role.role_id,
                    role_name=role.name,
                    actor_type=actor.get("type", ""),
                    actor_name=actor.get("displayName", actor.get("name", "")),
                    actor_id=actor.get("actorUser", {}).get("accountId")
                    or actor.get("actorGroup", {}).get("groupId"),
                ))
            return result
        except Exception:
            return []

    batch_results = await atlassian_client.batch(roles, _fetch_actors, concurrency=5)
    for _, role_actors in batch_results:
        if role_actors:
            actors.extend(role_actors)
    return actors


# ── Full Configuration Snapshot ──────────────────────

async def get_full_configuration() -> dict:
    """Fetch all Jira configuration entities concurrently."""
    (
        issue_types, statuses, priorities, resolutions,
        screens, screen_schemes, itss,
        field_configs, field_config_schemes,
        categories, roles,
    ) = await asyncio.gather(
        get_all_issue_types(),
        get_all_statuses(),
        get_all_priorities(),
        get_all_resolutions(),
        get_all_screens(),
        get_all_screen_schemes(),
        get_all_issue_type_screen_schemes(),
        get_all_field_configurations(),
        get_all_field_config_schemes(),
        get_all_project_categories(),
        get_all_project_roles(),
    )

    return {
        "issue_types": {"count": len(issue_types), "items": [i.model_dump() for i in issue_types]},
        "statuses": {"count": len(statuses), "items": [s.model_dump() for s in statuses]},
        "priorities": {"count": len(priorities), "items": [p.model_dump() for p in priorities]},
        "resolutions": {"count": len(resolutions), "items": [r.model_dump() for r in resolutions]},
        "screens": {"count": len(screens), "items": [s.model_dump() for s in screens]},
        "screen_schemes": {"count": len(screen_schemes), "items": [s.model_dump() for s in screen_schemes]},
        "issue_type_screen_schemes": {"count": len(itss), "items": [s.model_dump() for s in itss]},
        "field_configurations": {"count": len(field_configs), "items": [f.model_dump() for f in field_configs]},
        "field_config_schemes": {"count": len(field_config_schemes), "items": [s.model_dump() for s in field_config_schemes]},
        "project_categories": {"count": len(categories), "items": [c.model_dump() for c in categories]},
        "project_roles": {"count": len(roles), "items": [r.model_dump() for r in roles]},
    }
