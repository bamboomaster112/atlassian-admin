"""Track workflow and scheme usage across Jira projects."""

import asyncio
import logging
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import WorkflowUsage, SchemeUsage

logger = logging.getLogger(__name__)


async def get_all_workflows() -> list[WorkflowUsage]:
    """Fetch all workflows and their usage metrics."""
    workflows_raw = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/workflow/search"
    )
    workflows = []
    for wf in workflows_raw:
        statuses = [s.get("name", "") for s in wf.get("statuses", [])]
        transitions = len(wf.get("transitions", []))
        workflows.append(
            WorkflowUsage(
                workflow_name=wf.get("id", {}).get("name", wf.get("name", "")),
                projects_using=0,
                statuses=statuses,
                transitions=transitions,
            )
        )
    return workflows


async def get_workflow_scheme_mappings() -> list[SchemeUsage]:
    """Fetch workflow schemes and count project associations."""
    schemes_raw = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/workflowscheme"
    )
    return [
        SchemeUsage(
            scheme_name=s.get("name", ""),
            scheme_type="workflow",
            scheme_id=str(s.get("id", "")),
            is_default=s.get("defaultScheme", False),
        )
        for s in schemes_raw
    ]


async def get_permission_schemes() -> list[SchemeUsage]:
    """Fetch all permission schemes."""
    data = await atlassian_client.jira_get("/permissionscheme")
    return [
        SchemeUsage(
            scheme_name=s.get("name", ""),
            scheme_type="permission",
            scheme_id=str(s.get("id", "")),
        )
        for s in data.get("permissionSchemes", [])
    ]


async def get_notification_schemes() -> list[SchemeUsage]:
    """Fetch all notification schemes."""
    data = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/notificationscheme"
    )
    return [
        SchemeUsage(
            scheme_name=s.get("name", ""),
            scheme_type="notification",
            scheme_id=str(s.get("id", "")),
        )
        for s in data
    ]


async def get_issue_type_schemes() -> list[SchemeUsage]:
    """Fetch all issue type schemes."""
    data = await atlassian_client.get_paginated(
        f"{settings.jira_rest_url}/issuetypescheme"
    )
    return [
        SchemeUsage(
            scheme_name=s.get("name", ""),
            scheme_type="issue_type",
            scheme_id=str(s.get("id", "")),
            is_default=s.get("isDefault", False),
        )
        for s in data
    ]


async def get_all_schemes_summary() -> dict:
    """Aggregate all scheme types concurrently."""
    workflows, wf_schemes, perm_schemes, notif_schemes, it_schemes = await asyncio.gather(
        get_all_workflows(),
        get_workflow_scheme_mappings(),
        get_permission_schemes(),
        get_notification_schemes(),
        get_issue_type_schemes(),
    )

    return {
        "workflows": {"count": len(workflows), "items": [w.model_dump() for w in workflows]},
        "workflow_schemes": {"count": len(wf_schemes), "items": [s.model_dump() for s in wf_schemes]},
        "permission_schemes": {"count": len(perm_schemes), "items": [s.model_dump() for s in perm_schemes]},
        "notification_schemes": {"count": len(notif_schemes), "items": [s.model_dump() for s in notif_schemes]},
        "issue_type_schemes": {"count": len(it_schemes), "items": [s.model_dump() for s in it_schemes]},
    }
