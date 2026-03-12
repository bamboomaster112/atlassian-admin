"""Jira group management — groups, members, application roles."""

import logging
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import JiraGroup, GroupMember, ApplicationRole

logger = logging.getLogger(__name__)


async def get_all_groups() -> list[JiraGroup]:
    """Fetch all groups from the instance."""
    data = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/group/bulk"
    )
    return [
        JiraGroup(
            group_id=g.get("groupId", ""),
            name=g.get("name", ""),
        )
        for g in data
    ]


async def get_group_members(group_id: str, group_name: str) -> list[GroupMember]:
    """Fetch members of a specific group."""
    data = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/group/member",
        params={"groupId": group_id},
    )
    return [
        GroupMember(
            group_id=group_id,
            group_name=group_name,
            account_id=m.get("accountId", ""),
            display_name=m.get("displayName"),
            email=m.get("emailAddress"),
            active=m.get("active", True),
        )
        for m in data
    ]


async def get_all_groups_with_members() -> list[dict]:
    """Fetch all groups and their members (batched)."""
    groups = await get_all_groups()

    async def _fetch_members(group: JiraGroup):
        members = await get_group_members(group.group_id, group.name)
        return {
            "group": group.model_dump(),
            "members": [m.model_dump() for m in members],
            "member_count": len(members),
        }

    batch_results = await atlassian_client.batch(groups, _fetch_members, concurrency=5)

    results = []
    for group, data in batch_results:
        if data:
            results.append(data)
        else:
            results.append({
                "group": group.model_dump(),
                "members": [],
                "member_count": 0,
            })
    return results


async def get_application_roles() -> list[ApplicationRole]:
    """Fetch application roles (product access entitlements)."""
    try:
        data = await atlassian_client.jira_get("/applicationrole")
        return [
            ApplicationRole(
                role_key=r.get("key", ""),
                name=r.get("name", ""),
                user_count=r.get("userCount", 0),
                remaining_seats=r.get("remainingSeats"),
                groups=r.get("groups", []),
                default_groups=r.get("defaultGroups", []),
                has_unlimited_seats=r.get("hasUnlimitedSeats", False),
            )
            for r in data
        ]
    except Exception as e:
        logger.warning(f"Could not fetch application roles: {e}")
        return []
