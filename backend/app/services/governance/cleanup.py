"""Generate cleanup and optimization recommendations across all products."""

import asyncio
import logging
from datetime import datetime, timedelta
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import CleanupRecommendation
from ..jira.custom_fields import get_unused_custom_fields
from ..confluence.content import get_stale_content

logger = logging.getLogger(__name__)


async def recommend_unused_custom_fields() -> list[CleanupRecommendation]:
    """Flag custom fields with no usage."""
    try:
        unused = await get_unused_custom_fields()
    except Exception as e:
        logger.warning(f"Failed to fetch unused custom fields: {e}")
        return []

    return [
        CleanupRecommendation(
            category="custom_field",
            item_name=cf.field_name,
            item_id=cf.field_id,
            reason="Custom field is not populated in any issue",
            impact="low",
            product="jira",
        )
        for cf in unused
    ]


async def recommend_stale_confluence_pages(days: int = 365) -> list[CleanupRecommendation]:
    """Flag Confluence pages not updated in a long time."""
    try:
        stale = await get_stale_content(days=days, limit=50)
    except Exception as e:
        logger.warning(f"Failed to fetch stale content: {e}")
        return []

    return [
        CleanupRecommendation(
            category="content",
            item_name=page.title,
            item_id=page.content_id,
            reason=f"Page has not been updated in over {days} days",
            impact="low",
            product="confluence",
        )
        for page in stale
    ]


async def recommend_inactive_projects() -> list[CleanupRecommendation]:
    """Flag Jira projects with no recent activity (batched)."""
    projects = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/project/search", max_results=200
    )
    since = (datetime.utcnow() - timedelta(days=180)).strftime("%Y-%m-%d")

    async def _check_project(p):
        data = await atlassian_client.jira_get(
            "/search",
            params={
                "jql": f'project = {p["key"]} AND updated >= "{since}"',
                "maxResults": 0,
            },
        )
        return data.get("total", 0)

    batch_results = await atlassian_client.batch(projects, _check_project, concurrency=10)

    recs = []
    for project, total in batch_results:
        if total is not None and total == 0:
            recs.append(
                CleanupRecommendation(
                    category="project",
                    item_name=project.get("name", project["key"]),
                    item_id=project["key"],
                    reason="No issue activity in the last 180 days",
                    impact="medium",
                    product="jira",
                )
            )
    return recs


async def recommend_empty_confluence_spaces() -> list[CleanupRecommendation]:
    """Flag Confluence spaces with very few pages (batched)."""
    spaces = await atlassian_client.get_paginated(
        f"{settings.confluence_rest_url}/space", max_results=200
    )

    async def _check_space(s):
        content = await atlassian_client.confluence_get(
            f"/space/{s['key']}/content/page", params={"limit": 0},
        )
        return content.get("size", 0)

    batch_results = await atlassian_client.batch(spaces, _check_space, concurrency=10)

    recs = []
    for space, page_count in batch_results:
        if page_count is not None and page_count <= 1:
            recs.append(
                CleanupRecommendation(
                    category="space",
                    item_name=space.get("name", space["key"]),
                    item_id=space["key"],
                    reason=f"Space has only {page_count} page(s) — may be abandoned",
                    impact="low",
                    product="confluence",
                )
            )
    return recs


async def get_all_recommendations() -> dict:
    """Aggregate all cleanup recommendations concurrently."""
    cf_recs, stale_recs, project_recs, space_recs = await asyncio.gather(
        recommend_unused_custom_fields(),
        recommend_stale_confluence_pages(),
        recommend_inactive_projects(),
        recommend_empty_confluence_spaces(),
    )

    all_recs = cf_recs + stale_recs + project_recs + space_recs

    by_product: dict[str, list] = {}
    for r in all_recs:
        by_product.setdefault(r.product, []).append(r.model_dump())

    by_impact = {"low": 0, "medium": 0, "high": 0}
    for r in all_recs:
        by_impact[r.impact] = by_impact.get(r.impact, 0) + 1

    return {
        "total_recommendations": len(all_recs),
        "by_product": by_product,
        "by_impact": by_impact,
        "recommendations": [r.model_dump() for r in all_recs],
    }
