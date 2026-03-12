"""Jira audit log and instance info."""

import logging
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import AuditLogEntry, InstanceInfo

logger = logging.getLogger(__name__)


async def get_audit_records(limit: int = 200, filter_text: str | None = None) -> list[AuditLogEntry]:
    """Fetch recent audit log records from Jira."""
    params = {"limit": min(limit, 1000), "offset": 0}
    if filter_text:
        params["filter"] = filter_text

    try:
        data = await atlassian_client.jira_get("/auditing/record", params=params)
    except Exception as e:
        logger.warning(f"Could not fetch audit records: {e}")
        return []

    records = data.get("records", [])
    return [
        AuditLogEntry(
            audit_id=str(r.get("id", "")),
            summary=r.get("summary", ""),
            category=r.get("category"),
            event_source=r.get("eventSource"),
            author_id=r.get("authorAccountId"),
            author_name=r.get("authorKey"),
            object_type=r.get("objectItem", {}).get("typeName") if r.get("objectItem") else None,
            object_name=r.get("objectItem", {}).get("name") if r.get("objectItem") else None,
            object_id=r.get("objectItem", {}).get("id") if r.get("objectItem") else None,
            created=r.get("created"),
            changed_values=[
                {
                    "field_name": cv.get("fieldName", ""),
                    "changed_from": cv.get("changedFrom", ""),
                    "changed_to": cv.get("changedTo", ""),
                }
                for cv in r.get("changedValues", [])
            ],
            associated_items=[
                {
                    "id": ai.get("id", ""),
                    "name": ai.get("name", ""),
                    "type": ai.get("typeName", ""),
                }
                for ai in r.get("associatedItems", [])
            ],
        )
        for r in records
    ]


async def get_instance_info() -> InstanceInfo:
    """Fetch Jira server/instance info."""
    data = await atlassian_client.jira_get("/serverInfo")
    return InstanceInfo(
        base_url=data.get("baseUrl", settings.atlassian_base_url),
        version=data.get("version"),
        build_number=str(data.get("buildNumber", "")),
        deployment_type=data.get("deploymentType", "Cloud"),
        scm_info=data.get("scmInfo"),
        server_title=data.get("serverTitle"),
        default_locale=data.get("defaultLocale", {}).get("locale") if isinstance(data.get("defaultLocale"), dict) else data.get("defaultLocale"),
    )
