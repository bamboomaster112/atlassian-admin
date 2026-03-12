"""JSM organizations tracking."""

import logging
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import JSMOrganization

logger = logging.getLogger(__name__)


async def get_all_organizations() -> list[JSMOrganization]:
    """Fetch all JSM organizations."""
    try:
        data = await atlassian_client.get_paginated(
            f"{settings.jsm_rest_url}/organization"
        )
        return [
            JSMOrganization(
                org_id=str(o.get("id", "")),
                name=o.get("name", ""),
            )
            for o in data
        ]
    except Exception as e:
        logger.warning(f"Could not fetch JSM organizations: {e}")
        return []
