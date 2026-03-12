"""Cross-product license and user governance."""

from datetime import datetime
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import LicenseUsage, UserActivity


async def get_all_managed_users() -> list[UserActivity]:
    """Fetch users from the Atlassian admin org directory."""
    users_raw = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/users/search",
        max_results=5000,
    )
    users = []
    for u in users_raw:
        users.append(
            UserActivity(
                account_id=u["accountId"],
                display_name=u.get("displayName", ""),
                email=u.get("emailAddress"),
                active=u.get("active", False),
                product="all",
            )
        )
    return users


async def get_license_summary() -> list[LicenseUsage]:
    """Build a license usage summary per product."""
    users = await get_all_managed_users()
    active = [u for u in users if u.active]
    inactive = [u for u in users if not u.active]
    now = datetime.utcnow()

    # We report a combined view; individual product license counts
    # require Atlassian Admin API (org-level), which uses a different auth.
    return [
        LicenseUsage(
            product="jira",
            active_users=len(active),
            inactive_users=len(inactive),
            last_synced=now,
        ),
        LicenseUsage(
            product="confluence",
            active_users=len(active),
            inactive_users=len(inactive),
            last_synced=now,
        ),
        LicenseUsage(
            product="jira-service-management",
            active_users=len(active),
            inactive_users=len(inactive),
            last_synced=now,
        ),
    ]
