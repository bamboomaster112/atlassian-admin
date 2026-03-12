"""JSM service desk tracking — desks, request types, queues, SLAs."""

from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import (
    ServiceDeskSummary,
    RequestTypeUsage,
    QueueMetrics,
    SLAMetrics,
)


async def get_all_service_desks() -> list[ServiceDeskSummary]:
    """Fetch all JSM service desks."""
    desks_raw = await atlassian_client.get_paginated(
        f"{settings.jsm_rest_url}/servicedesk"
    )
    desks = []
    for d in desks_raw:
        desks.append(
            ServiceDeskSummary(
                service_desk_id=str(d["id"]),
                service_desk_name=d.get("projectName", ""),
                project_key=d.get("projectKey", ""),
            )
        )
    return desks


async def get_service_desk_detail(service_desk_id: str) -> ServiceDeskSummary:
    """Detailed metrics for a single service desk."""
    desk = await atlassian_client.jsm_get(f"/servicedesk/{service_desk_id}")

    # Request types
    rt_data = await atlassian_client.get_paginated(
        f"{settings.jsm_rest_url}/servicedesk/{service_desk_id}/requesttype"
    )

    # Queues
    queue_data = await atlassian_client.get_paginated(
        f"{settings.jsm_rest_url}/servicedesk/{service_desk_id}/queue"
    )

    # Customers
    customer_data = await atlassian_client.get_paginated(
        f"{settings.jsm_rest_url}/servicedesk/{service_desk_id}/customer"
    )

    return ServiceDeskSummary(
        service_desk_id=str(desk["id"]),
        service_desk_name=desk.get("projectName", ""),
        project_key=desk.get("projectKey", ""),
        request_types=len(rt_data),
        queues=len(queue_data),
        customers=len(customer_data),
    )


async def get_request_types(service_desk_id: str) -> list[RequestTypeUsage]:
    """Fetch all request types for a service desk."""
    rt_data = await atlassian_client.get_paginated(
        f"{settings.jsm_rest_url}/servicedesk/{service_desk_id}/requesttype"
    )
    request_types = []
    for rt in rt_data:
        # Get fields for this request type
        try:
            fields_data = await atlassian_client.jsm_get(
                f"/servicedesk/{service_desk_id}/requesttype/{rt['id']}/field"
            )
            field_names = [
                f.get("name", f.get("fieldId", ""))
                for f in fields_data.get("requestTypeFields", [])
            ]
        except Exception:
            field_names = []

        request_types.append(
            RequestTypeUsage(
                request_type_id=str(rt["id"]),
                request_type_name=rt.get("name", ""),
                service_desk_id=service_desk_id,
                fields=field_names,
            )
        )
    return request_types


async def get_queues(service_desk_id: str) -> list[QueueMetrics]:
    """Fetch queues and their issue counts."""
    queue_data = await atlassian_client.get_paginated(
        f"{settings.jsm_rest_url}/servicedesk/{service_desk_id}/queue"
    )
    queues = []
    for q in queue_data:
        issue_count = 0
        try:
            issues = await atlassian_client.jsm_get(
                f"/servicedesk/{service_desk_id}/queue/{q['id']}/issue",
                params={"limit": 0},
            )
            issue_count = issues.get("size", 0)
        except Exception:
            pass

        queues.append(
            QueueMetrics(
                queue_id=str(q["id"]),
                queue_name=q.get("name", ""),
                service_desk_id=service_desk_id,
                issue_count=issue_count,
                jql=q.get("jql"),
            )
        )
    return queues


async def get_jsm_overview() -> dict:
    """Cross-desk overview of all JSM service desks."""
    desks = await get_all_service_desks()
    details = []
    for desk in desks:
        detail = await get_service_desk_detail(desk.service_desk_id)
        details.append(detail.model_dump())

    return {
        "total_service_desks": len(details),
        "total_request_types": sum(d["request_types"] for d in details),
        "total_queues": sum(d["queues"] for d in details),
        "total_customers": sum(d["customers"] for d in details),
        "service_desks": details,
    }
