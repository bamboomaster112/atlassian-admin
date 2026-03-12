"""Jira user activity tracking — who is doing what and when."""

import asyncio
import logging
from datetime import datetime, timedelta
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import UserActivity

logger = logging.getLogger(__name__)


async def get_all_jira_users(active_only: bool = False) -> list[UserActivity]:
    """Fetch all Jira users with full profile data."""
    users_raw = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/users/search",
        max_results=5000,
    )
    users = []
    for u in users_raw:
        if active_only and not u.get("active", False):
            continue
        users.append(
            UserActivity(
                account_id=u.get("accountId", ""),
                display_name=u.get("displayName", ""),
                email=u.get("emailAddress"),
                active=u.get("active", False),
                account_type=u.get("accountType", "atlassian"),
                avatar_url=(u.get("avatarUrls", {}) or {}).get("48x48"),
                timezone=u.get("timeZone"),
                locale=u.get("locale"),
                product="jira",
            )
        )
    return users


async def get_user_activity(account_id: str, days: int = 30) -> UserActivity:
    """Compute activity metrics for a single user over the given window."""
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

    created_task = atlassian_client.jira_search(
        jql=f'creator = "{account_id}" AND created >= "{since}"', fields="key",
    )
    resolved_task = atlassian_client.jira_search(
        jql=f'assignee = "{account_id}" AND resolved >= "{since}"', fields="key",
    )
    updated_task = atlassian_client.jira_search(
        jql=f'updatedBy = "{account_id}" AND updated >= "{since}"', fields="key",
    )
    user_task = atlassian_client.jira_get(f"/user?accountId={account_id}")

    created, resolved, updated, user_info = await asyncio.gather(
        created_task, resolved_task, updated_task, user_task,
    )

    return UserActivity(
        account_id=account_id,
        display_name=user_info.get("displayName", ""),
        email=user_info.get("emailAddress"),
        active=user_info.get("active", False),
        account_type=user_info.get("accountType", "atlassian"),
        avatar_url=(user_info.get("avatarUrls", {}) or {}).get("48x48"),
        timezone=user_info.get("timeZone"),
        locale=user_info.get("locale"),
        issues_created=len(created),
        issues_resolved=len(resolved),
        issues_updated=len(updated),
        product="jira",
    )


async def get_inactive_users(days: int = 90) -> list[UserActivity]:
    """Return users who have not performed any Jira action in the given window."""
    all_users = await get_all_jira_users(active_only=True)
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

    async def _check_inactive(user: UserActivity):
        results = await atlassian_client.jira_search(
            jql=f'updatedBy = "{user.account_id}" AND updated >= "{since}"',
            fields="key",
            max_results=1,
        )
        return results

    batch_results = await atlassian_client.batch(all_users, _check_inactive, concurrency=10)
    return [user for user, results in batch_results if results is not None and len(results) == 0]


async def get_user_activity_summary(days: int = 30) -> dict:
    """High-level activity summary across all users."""
    all_users = await get_all_jira_users()
    active_count = sum(1 for u in all_users if u.active)
    inactive_count = len(all_users) - active_count

    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    created = await atlassian_client.jira_search(
        jql=f'created >= "{since}"', fields="creator", max_results=1000
    )

    creator_counts: dict[str, int] = {}
    for issue in created:
        creator = issue.get("fields", {}).get("creator", {}).get("displayName", "Unknown")
        creator_counts[creator] = creator_counts.get(creator, 0) + 1

    top_creators = sorted(creator_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total_users": len(all_users),
        "active_users": active_count,
        "inactive_users": inactive_count,
        "issues_created_last_n_days": len(created),
        "top_creators": [{"user": u, "count": c} for u, c in top_creators],
        "period_days": days,
    }
