"""Jira project-level analytics and tracking."""

import logging
from datetime import datetime, timedelta
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import ProjectSummary

logger = logging.getLogger(__name__)


async def get_all_projects() -> list[ProjectSummary]:
    """Fetch all Jira projects with full metadata."""
    projects_raw = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/project/search",
        params={"expand": "lead,description,projectCategory,issueTypes"},
    )
    projects = []
    for p in projects_raw:
        lead_name = None
        if p.get("lead"):
            lead_name = p["lead"].get("displayName")

        category = p.get("projectCategory")

        projects.append(
            ProjectSummary(
                project_id=str(p.get("id", "")),
                project_key=p["key"],
                project_name=p.get("name", ""),
                project_type=p.get("projectTypeKey", ""),
                description=p.get("description"),
                lead=lead_name,
                category_id=str(category["id"]) if category else None,
                category_name=category.get("name") if category else None,
                url=p.get("self"),
                avatar_url=(p.get("avatarUrls", {}) or {}).get("48x48"),
                simplified=p.get("simplified", False),
                is_private=p.get("isPrivate", False),
                style=p.get("style"),
            )
        )
    return projects


async def get_project_detail(project_key: str) -> ProjectSummary:
    """Deep analytics for a single project including scheme associations."""
    proj = await atlassian_client.jira_get(
        f"/project/{project_key}",
        params={"expand": "lead,description,projectCategory,issueTypes"},
    )

    # Issue count
    data = await atlassian_client.jira_get(
        "/search",
        params={"jql": f"project = {project_key}", "maxResults": 0},
    )
    total_from_search = data.get("total", 0)

    # Last created issue
    recent = await atlassian_client.jira_search(
        jql=f"project = {project_key} ORDER BY created DESC",
        fields="created",
        max_results=1,
    )
    last_created = None
    if recent:
        created_str = recent[0].get("fields", {}).get("created")
        if created_str:
            last_created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))

    # Active users in last 30 days
    since = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    active_issues = await atlassian_client.jira_search(
        jql=f'project = {project_key} AND updated >= "{since}"',
        fields="assignee,reporter",
        max_results=500,
    )
    user_ids: set[str] = set()
    for iss in active_issues:
        fields = iss.get("fields", {})
        for role in ("assignee", "reporter"):
            u = fields.get(role)
            if u and u.get("accountId"):
                user_ids.add(u["accountId"])

    lead_name = None
    if proj.get("lead"):
        lead_name = proj["lead"].get("displayName")

    category = proj.get("projectCategory")
    components = [
        {"id": str(c.get("id", "")), "name": c.get("name", "")}
        for c in proj.get("components", [])
    ]
    versions = [
        {
            "id": str(v.get("id", "")),
            "name": v.get("name", ""),
            "released": v.get("released", False),
            "archived": v.get("archived", False),
        }
        for v in proj.get("versions", [])
    ]

    return ProjectSummary(
        project_id=str(proj.get("id", "")),
        project_key=proj["key"],
        project_name=proj.get("name", ""),
        project_type=proj.get("projectTypeKey", ""),
        description=proj.get("description"),
        lead=lead_name,
        category_id=str(category["id"]) if category else None,
        category_name=category.get("name") if category else None,
        url=proj.get("self"),
        avatar_url=(proj.get("avatarUrls", {}) or {}).get("48x48"),
        simplified=proj.get("simplified", False),
        is_private=proj.get("isPrivate", False),
        style=proj.get("style"),
        issue_count=total_from_search,
        active_users=len(user_ids),
        last_issue_created=last_created,
        components=components,
        versions=versions,
    )


async def get_project_schemes(project_key: str) -> dict:
    """Fetch all scheme IDs associated with a project."""
    schemes = {}
    endpoints = [
        ("permission_scheme_id", f"/project/{project_key}/permissionscheme"),
        ("notification_scheme_id", f"/project/{project_key}/notificationscheme"),
    ]

    for key, path in endpoints:
        try:
            data = await atlassian_client.jira_get(path)
            schemes[key] = str(data.get("id", ""))
        except Exception:
            schemes[key] = None

    return schemes
