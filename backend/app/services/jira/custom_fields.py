"""Track custom field usage, identify unused or duplicate fields."""

from typing import Optional
from ...core.atlassian_client import atlassian_client
from ...core.config import settings
from ...models.schemas import CustomFieldUsage, CleanupRecommendation


async def get_all_custom_fields() -> list[CustomFieldUsage]:
    """Fetch every custom field definition from the instance."""
    fields_raw = await atlassian_client.jira_get("/field")
    custom_fields = []
    for f in fields_raw:
        if not f.get("custom", False):
            continue
        custom_fields.append(
            CustomFieldUsage(
                field_id=f["id"],
                field_name=f.get("name", ""),
                field_type=f.get("schema", {}).get("type", "unknown"),
            )
        )
    return custom_fields


async def get_custom_field_usage(field_id: str) -> CustomFieldUsage:
    """Analyse how heavily a single custom field is used."""
    field_info = None
    all_fields = await atlassian_client.jira_get("/field")
    for f in all_fields:
        if f["id"] == field_id:
            field_info = f
            break

    if not field_info:
        return CustomFieldUsage(field_id=field_id, field_name="Unknown", field_type="unknown")

    # Count issues where this field has a value
    issues = await atlassian_client.jira_search(
        jql=f'"{field_info["name"]}" is not EMPTY',
        fields="key",
        max_results=1000,
    )

    # Count projects where the field is populated
    project_keys: set[str] = set()
    if issues:
        sample = await atlassian_client.jira_search(
            jql=f'"{field_info["name"]}" is not EMPTY',
            fields="project",
            max_results=500,
        )
        for iss in sample:
            pk = iss.get("fields", {}).get("project", {}).get("key")
            if pk:
                project_keys.add(pk)

    # Screens using this field
    screens_count = 0
    try:
        screens = await atlassian_client.jira_get(f"/field/{field_id}/screens")
        screens_count = len(screens.get("values", []))
    except Exception:
        pass

    recommendation = None
    if len(issues) == 0:
        recommendation = "Unused — consider removing"
    elif len(issues) < 10:
        recommendation = "Very low usage — review necessity"

    return CustomFieldUsage(
        field_id=field_id,
        field_name=field_info.get("name", ""),
        field_type=field_info.get("schema", {}).get("type", "unknown"),
        projects_using=len(project_keys),
        issues_using=len(issues),
        screens_using=screens_count,
        recommendation=recommendation,
    )


async def get_unused_custom_fields() -> list[CustomFieldUsage]:
    """Return custom fields that appear to have zero usage."""
    all_fields = await get_all_custom_fields()
    unused = []
    for cf in all_fields:
        usage = await get_custom_field_usage(cf.field_id)
        if usage.issues_using == 0:
            unused.append(usage)
    return unused


async def get_custom_field_cleanup_recommendations() -> list[CleanupRecommendation]:
    """Generate actionable cleanup recommendations for custom fields."""
    unused = await get_unused_custom_fields()
    recs = []
    for cf in unused:
        recs.append(
            CleanupRecommendation(
                category="custom_field",
                item_name=cf.field_name,
                item_id=cf.field_id,
                reason="Custom field has zero issues with values",
                impact="low",
                product="jira",
            )
        )
    return recs
