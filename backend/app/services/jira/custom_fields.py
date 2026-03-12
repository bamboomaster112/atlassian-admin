"""Track custom field usage, identify unused or duplicate fields."""

import logging
from ...core.atlassian_client import atlassian_client
from ...models.schemas import CustomFieldUsage, CleanupRecommendation

logger = logging.getLogger(__name__)


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
    all_fields = await atlassian_client.jira_get("/field")
    field_info = next((f for f in all_fields if f["id"] == field_id), None)

    if not field_info:
        return CustomFieldUsage(field_id=field_id, field_name="Unknown", field_type="unknown")

    field_name = field_info.get("name", "")

    # Count issues where this field has a value
    try:
        issues = await atlassian_client.jira_search(
            jql=f'"{field_name}" is not EMPTY', fields="key", max_results=1000,
        )
    except Exception as e:
        logger.warning(f"Could not search for field '{field_name}': {e}")
        issues = []

    # Count projects where the field is populated
    project_keys: set[str] = set()
    if issues:
        try:
            sample = await atlassian_client.jira_search(
                jql=f'"{field_name}" is not EMPTY', fields="project", max_results=500,
            )
            for iss in sample:
                pk = iss.get("fields", {}).get("project", {}).get("key")
                if pk:
                    project_keys.add(pk)
        except Exception:
            pass

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
        field_name=field_name,
        field_type=field_info.get("schema", {}).get("type", "unknown"),
        projects_using=len(project_keys),
        issues_using=len(issues),
        screens_using=screens_count,
        recommendation=recommendation,
    )


async def get_unused_custom_fields() -> list[CustomFieldUsage]:
    """Return custom fields that appear to have zero usage (batched)."""
    all_fields = await get_all_custom_fields()

    async def _check_usage(cf: CustomFieldUsage):
        return await get_custom_field_usage(cf.field_id)

    batch_results = await atlassian_client.batch(all_fields, _check_usage, concurrency=5)

    return [usage for _, usage in batch_results if usage is not None and usage.issues_using == 0]


async def get_custom_field_cleanup_recommendations() -> list[CleanupRecommendation]:
    """Generate actionable cleanup recommendations for custom fields."""
    unused = await get_unused_custom_fields()
    return [
        CleanupRecommendation(
            category="custom_field",
            item_name=cf.field_name,
            item_id=cf.field_id,
            reason="Custom field has zero issues with values",
            impact="low",
            product="jira",
        )
        for cf in unused
    ]
