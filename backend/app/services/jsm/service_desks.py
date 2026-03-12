"""JSM service desk tracking — desks, request types, queues, SLAs."""

import asyncio
import logging
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import (
    ServiceDeskSummary,
    RequestTypeUsage,
    QueueMetrics,
)

logger = logging.getLogger(__name__)


async def get_all_service_desks() -> list[ServiceDeskSummary]:
    """Fetch all JSM service desks."""
    desks_raw = await atlassian_client.get_paginated(
        f"{settings.jsm_rest_url}/servicedesk"
    )
    return [
        ServiceDeskSummary(
            service_desk_id=str(d.get("id", "")),
            service_desk_name=d.get("projectName", ""),
            project_key=d.get("projectKey", ""),
        )
        for d in desks_raw
    ]


async def get_service_desk_detail(service_desk_id: str) -> ServiceDeskSummary:
    """Detailed metrics for a single service desk (concurrent sub-requests)."""
    desk = await atlassian_client.jsm_get(f"/servicedesk/{service_desk_id}")

    rt_task = atlassian_client.get_paginated(
        f"{settings.jsm_rest_url}/servicedesk/{service_desk_id}/requesttype"
    )
    queue_task = atlassian_client.get_paginated(
        f"{settings.jsm_rest_url}/servicedesk/{service_desk_id}/queue"
    )
    customer_task = atlassian_client.get_paginated(
        f"{settings.jsm_rest_url}/servicedesk/{service_desk_id}/customer"
    )

    results = await asyncio.gather(rt_task, queue_task, customer_task, return_exceptions=True)
    rt_data = results[0] if not isinstance(results[0], Exception) else []
    queue_data = results[1] if not isinstance(results[1], Exception) else []
    customer_data = results[2] if not isinstance(results[2], Exception) else []

    return ServiceDeskSummary(
        service_desk_id=str(desk.get("id", service_desk_id)),
        service_desk_name=desk.get("projectName", ""),
        project_key=desk.get("projectKey", ""),
        request_types=len(rt_data),
        queues=len(queue_data),
        customers=len(customer_data),
    )


async def get_request_types(service_desk_id: str) -> list[RequestTypeUsage]:
    """Fetch all request types with field details (batched)."""
    rt_data = await atlassian_client.get_paginated(
        f"{settings.jsm_rest_url}/servicedesk/{service_desk_id}/requesttype"
    )

    async def _fetch_fields(rt):
        try:
            fields_data = await atlassian_client.jsm_get(
                f"/servicedesk/{service_desk_id}/requesttype/{rt['id']}/field"
            )
            return [
                {
                    "fieldId": f.get("fieldId", ""),
                    "name": f.get("name", f.get("fieldId", "")),
                    "required": f.get("required", False),
                    "description": f.get("description", ""),
                }
                for f in fields_data.get("requestTypeFields", [])
            ]
        except Exception:
            return []

    batch_results = await atlassian_client.batch(rt_data, _fetch_fields, concurrency=5)

    return [
        RequestTypeUsage(
            request_type_id=str(rt.get("id", "")),
            request_type_name=rt.get("name", ""),
            service_desk_id=service_desk_id,
            description=rt.get("description"),
            help_text=rt.get("helpText"),
            icon_url=rt.get("icon", {}).get("url48x48") if rt.get("icon") else None,
            portal_id=str(rt.get("portalId", "")) if rt.get("portalId") else None,
            group_ids=[str(g) for g in rt.get("groupIds", [])],
            fields=field_data or [],
        )
        for rt, field_data in batch_results
    ]


async def get_queues(service_desk_id: str) -> list[QueueMetrics]:
    """Fetch queues and their issue counts (batched)."""
    queue_data = await atlassian_client.get_paginated(
        f"{settings.jsm_rest_url}/servicedesk/{service_desk_id}/queue"
    )

    async def _fetch_count(q):
        try:
            issues = await atlassian_client.jsm_get(
                f"/servicedesk/{service_desk_id}/queue/{q['id']}/issue",
                params={"limit": 0},
            )
            return issues.get("size", 0)
        except Exception:
            return 0

    batch_results = await atlassian_client.batch(queue_data, _fetch_count, concurrency=5)

    return [
        QueueMetrics(
            queue_id=str(q.get("id", "")),
            queue_name=q.get("name", ""),
            service_desk_id=service_desk_id,
            issue_count=count or 0,
            jql=q.get("jql"),
        )
        for q, count in batch_results
    ]


async def get_jsm_overview() -> dict:
    """Cross-desk overview of all JSM service desks (batched)."""
    desks = await get_all_service_desks()

    async def _detail(desk: ServiceDeskSummary):
        return await get_service_desk_detail(desk.service_desk_id)

    batch_results = await atlassian_client.batch(desks, _detail, concurrency=5)

    details = [d.model_dump() for _, d in batch_results if d is not None]

    return {
        "total_service_desks": len(details),
        "total_request_types": sum(d["request_types"] for d in details),
        "total_queues": sum(d["queues"] for d in details),
        "total_customers": sum(d["customers"] for d in details),
        "service_desks": details,
    }
