"""Confluence space analytics and tracking."""

import asyncio
import logging
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import SpaceAnalytics

logger = logging.getLogger(__name__)


async def get_all_spaces() -> list[SpaceAnalytics]:
    """Fetch all Confluence spaces with metadata."""
    spaces_raw = await atlassian_client.get_paginated(
        f"{settings.confluence_rest_url}/space",
        params={"expand": "description.plain,metadata.labels"},
    )
    return [
        SpaceAnalytics(
            space_key=s.get("key", ""),
            space_name=s.get("name", ""),
            space_type=s.get("type", "global"),
        )
        for s in spaces_raw
    ]


async def get_space_detail(space_key: str) -> SpaceAnalytics:
    """Detailed analytics for a single space."""
    space = await atlassian_client.confluence_get(
        f"/space/{space_key}",
        params={"expand": "description.plain,permissions"},
    )

    # Fetch page and blog counts concurrently
    pages_task = atlassian_client.confluence_get(
        f"/space/{space_key}/content/page", params={"limit": 0},
    )
    blogs_task = atlassian_client.confluence_get(
        f"/space/{space_key}/content/blogpost", params={"limit": 0},
    )

    try:
        pages, blogs = await asyncio.gather(pages_task, blogs_task)
    except Exception as e:
        logger.warning(f"Failed to fetch content counts for space {space_key}: {e}")
        pages, blogs = {}, {}

    total_pages = pages.get("size", 0)
    total_blogs = blogs.get("size", 0)

    # Permissions summary
    perms = space.get("permissions", [])
    perm_summary = {}
    for p in perms:
        subjects = p.get("subjects", {})
        for subject_type in ("user", "group"):
            for subj in subjects.get(subject_type, {}).get("results", []):
                name = subj.get("displayName", subj.get("name", "unknown"))
                key = f"{subject_type}:{name}"
                if key not in perm_summary:
                    perm_summary[key] = []
                perm_summary[key].append(p.get("operation", {}).get("operation", ""))

    return SpaceAnalytics(
        space_key=space.get("key", space_key),
        space_name=space.get("name", ""),
        space_type=space.get("type", "global"),
        total_pages=total_pages,
        total_blog_posts=total_blogs,
        permissions_summary=perm_summary,
    )


async def get_space_growth_summary() -> dict:
    """Overview of all spaces with page counts (batched)."""
    spaces = await get_all_spaces()

    async def _detail(space: SpaceAnalytics):
        return await get_space_detail(space.space_key)

    batch_results = await atlassian_client.batch(spaces, _detail, concurrency=5)

    summaries = [
        detail.model_dump()
        for _, detail in batch_results
        if detail is not None
    ]

    total_pages = sum(s["total_pages"] for s in summaries)
    total_blogs = sum(s["total_blog_posts"] for s in summaries)

    return {
        "total_spaces": len(summaries),
        "total_pages": total_pages,
        "total_blog_posts": total_blogs,
        "spaces": summaries,
    }
