"""Confluence space analytics and tracking."""

from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import SpaceAnalytics


async def get_all_spaces() -> list[SpaceAnalytics]:
    """Fetch all Confluence spaces with metadata."""
    spaces_raw = await atlassian_client.get_paginated(
        f"{settings.confluence_rest_url}/space",
        params={"expand": "description.plain,metadata.labels"},
    )
    spaces = []
    for s in spaces_raw:
        spaces.append(
            SpaceAnalytics(
                space_key=s["key"],
                space_name=s.get("name", ""),
                space_type=s.get("type", "global"),
            )
        )
    return spaces


async def get_space_detail(space_key: str) -> SpaceAnalytics:
    """Detailed analytics for a single space."""
    space = await atlassian_client.confluence_get(
        f"/space/{space_key}",
        params={"expand": "description.plain,permissions"},
    )

    # Count pages
    pages = await atlassian_client.confluence_get(
        f"/space/{space_key}/content/page",
        params={"limit": 0},
    )
    total_pages = pages.get("size", 0)

    # Count blog posts
    blogs = await atlassian_client.confluence_get(
        f"/space/{space_key}/content/blogpost",
        params={"limit": 0},
    )
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
        space_key=space["key"],
        space_name=space.get("name", ""),
        space_type=space.get("type", "global"),
        total_pages=total_pages,
        total_blog_posts=total_blogs,
        permissions_summary=perm_summary,
    )


async def get_space_growth_summary() -> dict:
    """Overview of all spaces with page counts."""
    spaces = await get_all_spaces()
    summaries = []
    for s in spaces:
        detail = await get_space_detail(s.space_key)
        summaries.append(detail.model_dump())

    total_pages = sum(s["total_pages"] for s in summaries)
    total_blogs = sum(s["total_blog_posts"] for s in summaries)

    return {
        "total_spaces": len(summaries),
        "total_pages": total_pages,
        "total_blog_posts": total_blogs,
        "spaces": summaries,
    }
