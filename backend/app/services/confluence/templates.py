"""Confluence template tracking."""

import logging
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import ConfluenceTemplate

logger = logging.getLogger(__name__)


async def get_all_templates() -> list[ConfluenceTemplate]:
    """Fetch all content templates (global + space-level)."""
    templates = []

    # Global templates
    try:
        data = await atlassian_client.confluence_get(
            "/template/page",
            params={"expand": "body,labels", "limit": 200},
        )
        for t in data.get("results", []):
            labels = [lb.get("name", "") for lb in t.get("labels", [])]
            templates.append(ConfluenceTemplate(
                template_id=str(t.get("templateId", "")),
                name=t.get("name", ""),
                description=t.get("description"),
                template_type=t.get("templateType", "page"),
                space_key=t.get("space", {}).get("key") if t.get("space") else None,
                body_format=t.get("body", {}).get("representation", "storage"),
                labels=labels,
            ))
    except Exception as e:
        logger.warning(f"Could not fetch templates: {e}")

    return templates
