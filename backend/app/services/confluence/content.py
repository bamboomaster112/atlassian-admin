"""Confluence content analytics — stale pages, heavy contributors, labels."""

import logging
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import ContentAnalytics

logger = logging.getLogger(__name__)


async def get_recently_updated_content(days: int = 30, limit: int = 50) -> list[ContentAnalytics]:
    """Fetch recently updated pages/blogs across the instance."""
    cql = f'lastModified >= now("-{days}d") ORDER BY lastModified DESC'
    results = await atlassian_client.confluence_get(
        "/content/search",
        params={"cql": cql, "limit": limit, "expand": "version,space,metadata.labels"},
    )
    items = []
    for r in results.get("results", []):
        labels = [
            lb["name"]
            for lb in r.get("metadata", {}).get("labels", {}).get("results", [])
        ]
        items.append(
            ContentAnalytics(
                content_id=r["id"],
                title=r.get("title", ""),
                space_key=r.get("space", {}).get("key", ""),
                content_type=r.get("type", "page"),
                version=r.get("version", {}).get("number", 1),
                labels=labels,
            )
        )
    return items


async def get_stale_content(days: int = 365, limit: int = 100) -> list[ContentAnalytics]:
    """Identify pages not updated for a long time."""
    cql = f'lastModified <= now("-{days}d") AND type = page ORDER BY lastModified ASC'
    results = await atlassian_client.confluence_get(
        "/content/search",
        params={"cql": cql, "limit": limit, "expand": "version,space"},
    )
    return [
        ContentAnalytics(
            content_id=r["id"],
            title=r.get("title", ""),
            space_key=r.get("space", {}).get("key", ""),
            content_type="page",
            version=r.get("version", {}).get("number", 1),
        )
        for r in results.get("results", [])
    ]


async def get_top_contributors(days: int = 30, limit: int = 20) -> list[dict]:
    """Identify most active Confluence contributors."""
    cql = f'lastModified >= now("-{days}d")'
    results = await atlassian_client.confluence_get(
        "/content/search",
        params={"cql": cql, "limit": 500, "expand": "version"},
    )
    contributor_counts: dict[str, int] = {}
    for r in results.get("results", []):
        author = r.get("version", {}).get("by", {}).get("displayName", "Unknown")
        contributor_counts[author] = contributor_counts.get(author, 0) + 1

    sorted_contributors = sorted(contributor_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"user": u, "edits": c} for u, c in sorted_contributors[:limit]]


async def get_label_usage() -> list[dict]:
    """Aggregate label usage across the instance (batched)."""
    spaces_raw = await atlassian_client.get_paginated(
        f"{settings.confluence_rest_url}/space"
    )

    async def _fetch_labels(space):
        content = await atlassian_client.confluence_get(
            f"/space/{space['key']}/content/page",
            params={"limit": 200, "expand": "metadata.labels"},
        )
        counts: dict[str, int] = {}
        for page in content.get("results", []):
            for label in page.get("metadata", {}).get("labels", {}).get("results", []):
                name = label.get("name", "")
                if name:
                    counts[name] = counts.get(name, 0) + 1
        return counts

    batch_results = await atlassian_client.batch(
        spaces_raw[:50], _fetch_labels, concurrency=5
    )

    # Merge all space-level counts
    label_counts: dict[str, int] = {}
    for _, counts in batch_results:
        if counts:
            for name, count in counts.items():
                label_counts[name] = label_counts.get(name, 0) + count

    sorted_labels = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"label": name, "count": count} for name, count in sorted_labels]
