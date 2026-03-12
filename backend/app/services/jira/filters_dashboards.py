"""Jira saved filters and dashboards tracking."""

import asyncio
import logging
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import JiraFilter, JiraDashboard

logger = logging.getLogger(__name__)


async def get_all_filters() -> list[JiraFilter]:
    """Fetch all shared/favourite filters from the instance."""
    data = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/filter/search",
        params={"expand": "description,owner,jql,sharePermissions,subscriptions"},
    )
    return [
        JiraFilter(
            filter_id=str(f.get("id", "")),
            name=f.get("name", ""),
            description=f.get("description"),
            owner_account_id=f.get("owner", {}).get("accountId"),
            owner_display_name=f.get("owner", {}).get("displayName"),
            jql=f.get("jql"),
            is_favourite=f.get("favourite", False),
            favourite_count=f.get("favouritedCount", 0),
            share_permissions=[
                {
                    "type": sp.get("type", ""),
                    "project_id": sp.get("project", {}).get("id") if sp.get("project") else None,
                    "group_name": sp.get("group", {}).get("name") if sp.get("group") else None,
                    "role_id": sp.get("role", {}).get("id") if sp.get("role") else None,
                }
                for sp in f.get("sharePermissions", [])
            ],
            subscriptions=[
                {"id": str(s.get("id", "")), "user": s.get("user", {}).get("displayName")}
                for s in f.get("subscriptions", {}).get("items", [])
            ],
        )
        for f in data
    ]


async def get_all_dashboards() -> list[JiraDashboard]:
    """Fetch all dashboards from the instance."""
    data = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/dashboard/search",
    )

    async def _fetch_gadgets(dash):
        try:
            gadgets_data = await atlassian_client.jira_get(
                f"/dashboard/{dash['id']}/gadget"
            )
            return [
                {
                    "id": str(g.get("id", "")),
                    "title": g.get("title", ""),
                    "module_key": g.get("moduleKey", ""),
                    "uri": g.get("uri", ""),
                }
                for g in gadgets_data.get("gadgets", [])
            ]
        except Exception:
            return []

    batch_results = await atlassian_client.batch(data, _fetch_gadgets, concurrency=5)

    dashboards = []
    for d, gadgets in batch_results:
        owner = d.get("owner", {})
        dashboards.append(
            JiraDashboard(
                dashboard_id=str(d.get("id", "")),
                name=d.get("name", ""),
                description=d.get("description"),
                owner_account_id=owner.get("accountId") if owner else None,
                owner_display_name=owner.get("displayName") if owner else None,
                is_system=d.get("systemDashboard", False),
                is_favourite=d.get("isFavourite", False),
                share_permissions=[
                    {
                        "type": sp.get("type", ""),
                        "project_id": sp.get("project", {}).get("id") if sp.get("project") else None,
                        "group_name": sp.get("group", {}).get("name") if sp.get("group") else None,
                    }
                    for sp in d.get("sharePermissions", [])
                ],
                gadgets=gadgets or [],
            )
        )
    return dashboards


async def get_filters_dashboards_summary() -> dict:
    """Concurrent fetch of both filters and dashboards."""
    filters, dashboards = await asyncio.gather(
        get_all_filters(),
        get_all_dashboards(),
    )
    return {
        "filters": {"count": len(filters), "items": [f.model_dump() for f in filters]},
        "dashboards": {"count": len(dashboards), "items": [d.model_dump() for d in dashboards]},
    }
