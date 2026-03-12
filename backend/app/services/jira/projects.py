"""Jira project-level analytics and tracking."""

from datetime import datetime, timedelta
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import ProjectSummary


async def get_all_projects() -> list[ProjectSummary]:
    """Fetch all Jira projects with basic metadata."""
    projects_raw = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/project/search",
        params={"expand": "lead"},
    )
    projects = []
    for p in projects_raw:
        lead_name = None
        if p.get("lead"):
            lead_name = p["lead"].get("displayName")
        projects.append(
            ProjectSummary(
                project_key=p["key"],
                project_name=p.get("name", ""),
                project_type=p.get("projectTypeKey", ""),
                lead=lead_name,
            )
        )
    return projects


async def get_project_detail(project_key: str) -> ProjectSummary:
    """Deep analytics for a single project."""
    proj = await atlassian_client.jira_get(f"/project/{project_key}")

    # Issue count
    search = await atlassian_client.jira_search(
        jql=f"project = {project_key}", fields="key", max_results=1
    )
    total_from_search = 0
    if search:
        # The search endpoint returns total in the wrapper
        data = await atlassian_client.jira_get(
            f"/search",
            params={"jql": f"project = {project_key}", "maxResults": 0},
        )
        total_from_search = data.get("total", 0)

    # Recent issues to find last created
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

    return ProjectSummary(
        project_key=proj["key"],
        project_name=proj.get("name", ""),
        project_type=proj.get("projectTypeKey", ""),
        lead=lead_name,
        issue_count=total_from_search,
        active_users=len(user_ids),
        last_issue_created=last_created,
    )
