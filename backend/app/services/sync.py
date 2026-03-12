"""Sync engine — fetches data from Atlassian APIs and persists to Supabase."""

from datetime import datetime, timezone
from ..core.database import get_supabase

# Re-export for convenience — this module is only imported inside functions
# to avoid circular imports.


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log_sync(category: str, count: int, status: str = "success", error: str | None = None):
    sb = get_supabase()
    sb.table("sync_history").insert({
        "category": category,
        "record_count": count,
        "status": status,
        "error_message": error,
        "synced_at": _now(),
    }).execute()


# ── Jira Users ────────────────────────────────────────

async def sync_jira_users():
    from .jira.user_tracking import get_all_jira_users
    try:
        users = await get_all_jira_users()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "account_id": u.account_id,
                "display_name": u.display_name,
                "email": u.email,
                "active": u.active,
                "issues_created": u.issues_created,
                "issues_resolved": u.issues_resolved,
                "issues_updated": u.issues_updated,
                "comments_count": u.comments_count,
                "synced_at": now,
            }
            for u in users
        ]
        if rows:
            sb.table("jira_users").insert(rows).execute()
        _log_sync("jira_users", len(rows))
        return rows
    except Exception as e:
        _log_sync("jira_users", 0, "error", str(e))
        raise


# ── Custom Fields ─────────────────────────────────────

async def sync_custom_fields():
    from .jira.custom_fields import get_all_custom_fields
    try:
        fields = await get_all_custom_fields()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "field_id": f.field_id,
                "field_name": f.field_name,
                "field_type": f.field_type,
                "projects_using": f.projects_using,
                "issues_using": f.issues_using,
                "screens_using": f.screens_using,
                "is_required": f.is_required,
                "recommendation": f.recommendation,
                "synced_at": now,
            }
            for f in fields
        ]
        if rows:
            sb.table("custom_fields").insert(rows).execute()
        _log_sync("custom_fields", len(rows))
        return rows
    except Exception as e:
        _log_sync("custom_fields", 0, "error", str(e))
        raise


# ── Projects ──────────────────────────────────────────

async def sync_jira_projects():
    from .jira.projects import get_all_projects
    try:
        projects = await get_all_projects()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "project_key": p.project_key,
                "project_name": p.project_name,
                "project_type": p.project_type,
                "lead": p.lead,
                "issue_count": p.issue_count,
                "active_users": p.active_users,
                "last_issue_created": p.last_issue_created.isoformat() if p.last_issue_created else None,
                "synced_at": now,
            }
            for p in projects
        ]
        if rows:
            sb.table("jira_projects").insert(rows).execute()
        _log_sync("jira_projects", len(rows))
        return rows
    except Exception as e:
        _log_sync("jira_projects", 0, "error", str(e))
        raise


# ── Confluence Spaces ─────────────────────────────────

async def sync_confluence_spaces():
    from .confluence.spaces import get_all_spaces
    try:
        spaces = await get_all_spaces()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "space_key": s.space_key,
                "space_name": s.space_name,
                "space_type": s.space_type,
                "total_pages": s.total_pages,
                "total_blog_posts": s.total_blog_posts,
                "total_attachments": s.total_attachments,
                "attachment_size_mb": s.attachment_size_mb,
                "active_contributors": s.active_contributors,
                "synced_at": now,
            }
            for s in spaces
        ]
        if rows:
            sb.table("confluence_spaces").insert(rows).execute()
        _log_sync("confluence_spaces", len(rows))
        return rows
    except Exception as e:
        _log_sync("confluence_spaces", 0, "error", str(e))
        raise


# ── JSM Service Desks ────────────────────────────────

async def sync_jsm_service_desks():
    from .jsm.service_desks import get_all_service_desks
    try:
        desks = await get_all_service_desks()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "service_desk_id": d.service_desk_id,
                "service_desk_name": d.service_desk_name,
                "project_key": d.project_key,
                "request_types": d.request_types,
                "queues": d.queues,
                "open_requests": d.open_requests,
                "customers": d.customers,
                "synced_at": now,
            }
            for d in desks
        ]
        if rows:
            sb.table("jsm_service_desks").insert(rows).execute()
        _log_sync("jsm_service_desks", len(rows))
        return rows
    except Exception as e:
        _log_sync("jsm_service_desks", 0, "error", str(e))
        raise


# ── Cleanup Recommendations ──────────────────────────

async def sync_cleanup_recommendations():
    from .governance.cleanup import get_all_recommendations
    try:
        recs = await get_all_recommendations()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "category": r["category"],
                "item_name": r["item_name"],
                "item_id": r["item_id"],
                "reason": r["reason"],
                "impact": r["impact"],
                "product": r["product"],
                "synced_at": now,
            }
            for r in recs.get("recommendations", [])
        ]
        if rows:
            sb.table("cleanup_recommendations").insert(rows).execute()
        _log_sync("cleanup_recommendations", len(rows))
        return rows
    except Exception as e:
        _log_sync("cleanup_recommendations", 0, "error", str(e))
        raise


# ── Permissions Audit ─────────────────────────────────

async def sync_permissions_audit():
    from .governance.permissions_audit import get_full_permissions_audit
    try:
        audit = await get_full_permissions_audit()
        sb = get_supabase()
        now = _now()
        all_entries = (
            audit.get("jira_global_permissions", [])
            + audit.get("jira_project_permissions", [])
            + audit.get("confluence_space_permissions", [])
        )
        rows = [
            {
                "entity_type": e["entity_type"],
                "entity_name": e["entity_name"],
                "product": e["product"],
                "scope": e["scope"],
                "scope_key": e.get("scope_key"),
                "permissions": e.get("permissions", []),
                "synced_at": now,
            }
            for e in all_entries
        ]
        if rows:
            sb.table("permissions_audit").insert(rows).execute()
        _log_sync("permissions_audit", len(rows))
        return rows
    except Exception as e:
        _log_sync("permissions_audit", 0, "error", str(e))
        raise


# ── License Usage ─────────────────────────────────────

async def sync_license_usage():
    from .governance.license_tracking import get_license_summary
    try:
        licenses = await get_license_summary()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "product": lic.product,
                "total_licenses": lic.total_licenses,
                "active_users": lic.active_users,
                "inactive_users": lic.inactive_users,
                "synced_at": now,
            }
            for lic in licenses
        ]
        if rows:
            sb.table("license_usage").insert(rows).execute()
        _log_sync("license_usage", len(rows))
        return rows
    except Exception as e:
        _log_sync("license_usage", 0, "error", str(e))
        raise


# ── Dashboard Snapshot ────────────────────────────────

async def sync_dashboard_snapshot():
    """Save a point-in-time dashboard snapshot for trend analysis."""
    from .jira.projects import get_all_projects
    from .jira.custom_fields import get_all_custom_fields, get_unused_custom_fields
    from .jira.user_tracking import get_all_jira_users
    from .confluence.spaces import get_all_spaces
    from .jsm.service_desks import get_all_service_desks

    try:
        projects = await get_all_projects()
        spaces = await get_all_spaces()
        desks = await get_all_service_desks()
        users = await get_all_jira_users()
        cfs = await get_all_custom_fields()
        unused_cfs = await get_unused_custom_fields()

        active = sum(1 for u in users if u.active)
        sb = get_supabase()
        row = {
            "jira_projects": len(projects),
            "confluence_spaces": len(spaces),
            "jsm_service_desks": len(desks),
            "total_users": len(users),
            "active_users": active,
            "inactive_users": len(users) - active,
            "custom_fields_total": len(cfs),
            "custom_fields_unused": len(unused_cfs),
            "synced_at": _now(),
        }
        sb.table("dashboard_snapshots").insert(row).execute()
        _log_sync("dashboard_snapshot", 1)
        return row
    except Exception as e:
        _log_sync("dashboard_snapshot", 0, "error", str(e))
        raise


# ── Full Sync ─────────────────────────────────────────

async def run_full_sync():
    """Run all sync operations. Called by scheduler or manual trigger."""
    results = {}
    for name, fn in [
        ("jira_users", sync_jira_users),
        ("custom_fields", sync_custom_fields),
        ("jira_projects", sync_jira_projects),
        ("confluence_spaces", sync_confluence_spaces),
        ("jsm_service_desks", sync_jsm_service_desks),
        ("cleanup_recommendations", sync_cleanup_recommendations),
        ("permissions_audit", sync_permissions_audit),
        ("license_usage", sync_license_usage),
        ("dashboard_snapshot", sync_dashboard_snapshot),
    ]:
        try:
            results[name] = {"status": "success", "data": await fn()}
        except Exception as e:
            results[name] = {"status": "error", "error": str(e)}
    return results
