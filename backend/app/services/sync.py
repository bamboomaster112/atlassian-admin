"""Sync engine — fetches data from Atlassian APIs and persists to Supabase."""

import asyncio
import logging
from datetime import datetime, timezone
from ..core.database import get_supabase

logger = logging.getLogger(__name__)


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
                "account_type": u.account_type,
                "avatar_url": u.avatar_url,
                "timezone": u.timezone,
                "locale": u.locale,
                "last_active": u.last_active.isoformat() if u.last_active else None,
                "issues_created": u.issues_created,
                "issues_resolved": u.issues_resolved,
                "issues_updated": u.issues_updated,
                "comments_count": u.comments_count,
                "groups": u.groups,
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
                "description": f.description,
                "searcher_key": f.searcher_key,
                "schema_type": f.schema_type,
                "schema_custom": f.schema_custom,
                "schema_custom_id": f.schema_custom_id,
                "projects_using": f.projects_using,
                "issues_using": f.issues_using,
                "screens_using": f.screens_using,
                "is_required": f.is_required,
                "is_locked": f.is_locked,
                "is_managed": f.is_managed,
                "context_project_ids": f.context_project_ids,
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
                "project_id": p.project_id,
                "project_key": p.project_key,
                "project_name": p.project_name,
                "project_type": p.project_type,
                "description": p.description,
                "lead": p.lead,
                "category_id": p.category_id,
                "category_name": p.category_name,
                "url": p.url,
                "avatar_url": p.avatar_url,
                "simplified": p.simplified,
                "is_private": p.is_private,
                "style": p.style,
                "issue_count": p.issue_count,
                "active_users": p.active_users,
                "last_issue_created": p.last_issue_created.isoformat() if p.last_issue_created else None,
                "permission_scheme_id": p.permission_scheme_id,
                "notification_scheme_id": p.notification_scheme_id,
                "issue_type_scheme_id": p.issue_type_scheme_id,
                "workflow_scheme_id": p.workflow_scheme_id,
                "field_config_scheme_id": p.field_config_scheme_id,
                "issue_type_screen_scheme_id": p.issue_type_screen_scheme_id,
                "components": p.components,
                "versions": p.versions,
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


# ── Workflows ─────────────────────────────────────────

async def sync_workflows():
    from .jira.workflows import get_all_workflows
    try:
        workflows = await get_all_workflows()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "workflow_id": w.workflow_id,
                "workflow_name": w.workflow_name,
                "description": w.description,
                "scope": w.scope,
                "projects_using": w.projects_using,
                "statuses": w.statuses,
                "transitions": w.transitions,
                "transition_details": w.transition_details,
                "is_default": w.is_default,
                "synced_at": now,
            }
            for w in workflows
        ]
        if rows:
            sb.table("workflows").insert(rows).execute()
        _log_sync("workflows", len(rows))
        return rows
    except Exception as e:
        _log_sync("workflows", 0, "error", str(e))
        raise


# ── Schemes ───────────────────────────────────────────

async def sync_schemes():
    from .jira.workflows import (
        get_workflow_scheme_mappings, get_permission_schemes,
        get_notification_schemes, get_issue_type_schemes,
    )
    try:
        wf, perm, notif, it = await asyncio.gather(
            get_workflow_scheme_mappings(),
            get_permission_schemes(),
            get_notification_schemes(),
            get_issue_type_schemes(),
        )
        all_schemes = wf + perm + notif + it
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "scheme_name": s.scheme_name,
                "scheme_type": s.scheme_type,
                "scheme_id": s.scheme_id,
                "description": s.description,
                "projects_using": s.projects_using,
                "project_ids": s.project_ids,
                "is_default": s.is_default,
                "synced_at": now,
            }
            for s in all_schemes
        ]
        if rows:
            sb.table("schemes").insert(rows).execute()
        _log_sync("schemes", len(rows))
        return rows
    except Exception as e:
        _log_sync("schemes", 0, "error", str(e))
        raise


# ── Issue Types ───────────────────────────────────────

async def sync_issue_types():
    from .jira.configuration import get_all_issue_types
    try:
        items = await get_all_issue_types()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "issue_type_id": i.issue_type_id,
                "name": i.name,
                "description": i.description,
                "icon_url": i.icon_url,
                "subtask": i.subtask,
                "hierarchy_level": i.hierarchy_level,
                "scope": i.scope,
                "avatar_id": i.avatar_id,
                "synced_at": now,
            }
            for i in items
        ]
        if rows:
            sb.table("jira_issue_types").insert(rows).execute()
        _log_sync("issue_types", len(rows))
        return rows
    except Exception as e:
        _log_sync("issue_types", 0, "error", str(e))
        raise


# ── Statuses ──────────────────────────────────────────

async def sync_statuses():
    from .jira.configuration import get_all_statuses
    try:
        items = await get_all_statuses()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "status_id": s.status_id,
                "name": s.name,
                "description": s.description,
                "status_category": s.status_category,
                "status_category_id": s.status_category_id,
                "scope": s.scope,
                "usages": s.usages,
                "synced_at": now,
            }
            for s in items
        ]
        if rows:
            sb.table("jira_statuses").insert(rows).execute()
        _log_sync("statuses", len(rows))
        return rows
    except Exception as e:
        _log_sync("statuses", 0, "error", str(e))
        raise


# ── Priorities ────────────────────────────────────────

async def sync_priorities():
    from .jira.configuration import get_all_priorities
    try:
        items = await get_all_priorities()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "priority_id": p.priority_id,
                "name": p.name,
                "description": p.description,
                "icon_url": p.icon_url,
                "status_color": p.status_color,
                "is_default": p.is_default,
                "sort_order": idx,
                "synced_at": now,
            }
            for idx, p in enumerate(items)
        ]
        if rows:
            sb.table("jira_priorities").insert(rows).execute()
        _log_sync("priorities", len(rows))
        return rows
    except Exception as e:
        _log_sync("priorities", 0, "error", str(e))
        raise


# ── Resolutions ───────────────────────────────────────

async def sync_resolutions():
    from .jira.configuration import get_all_resolutions
    try:
        items = await get_all_resolutions()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "resolution_id": r.resolution_id,
                "name": r.name,
                "description": r.description,
                "is_default": r.is_default,
                "synced_at": now,
            }
            for r in items
        ]
        if rows:
            sb.table("jira_resolutions").insert(rows).execute()
        _log_sync("resolutions", len(rows))
        return rows
    except Exception as e:
        _log_sync("resolutions", 0, "error", str(e))
        raise


# ── Screens ───────────────────────────────────────────

async def sync_screens():
    from .jira.configuration import get_all_screens
    try:
        items = await get_all_screens()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "screen_id": s.screen_id,
                "name": s.name,
                "description": s.description,
                "scope": s.scope,
                "tab_count": s.tab_count,
                "tabs": s.tabs,
                "synced_at": now,
            }
            for s in items
        ]
        if rows:
            sb.table("jira_screens").insert(rows).execute()
        _log_sync("screens", len(rows))
        return rows
    except Exception as e:
        _log_sync("screens", 0, "error", str(e))
        raise


# ── Screen Schemes ────────────────────────────────────

async def sync_screen_schemes():
    from .jira.configuration import get_all_screen_schemes
    try:
        items = await get_all_screen_schemes()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "scheme_id": s.scheme_id,
                "name": s.name,
                "description": s.description,
                "screens": s.screens,
                "synced_at": now,
            }
            for s in items
        ]
        if rows:
            sb.table("jira_screen_schemes").insert(rows).execute()
        _log_sync("screen_schemes", len(rows))
        return rows
    except Exception as e:
        _log_sync("screen_schemes", 0, "error", str(e))
        raise


# ── Issue Type Screen Schemes ─────────────────────────

async def sync_issue_type_screen_schemes():
    from .jira.configuration import get_all_issue_type_screen_schemes
    try:
        items = await get_all_issue_type_screen_schemes()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "scheme_id": s.scheme_id,
                "name": s.name,
                "description": s.description,
                "mappings": s.mappings,
                "synced_at": now,
            }
            for s in items
        ]
        if rows:
            sb.table("jira_issue_type_screen_schemes").insert(rows).execute()
        _log_sync("issue_type_screen_schemes", len(rows))
        return rows
    except Exception as e:
        _log_sync("issue_type_screen_schemes", 0, "error", str(e))
        raise


# ── Field Configurations ──────────────────────────────

async def sync_field_configurations():
    from .jira.configuration import get_all_field_configurations
    try:
        items = await get_all_field_configurations()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "config_id": fc.config_id,
                "name": fc.name,
                "description": fc.description,
                "is_default": fc.is_default,
                "fields": fc.fields,
                "synced_at": now,
            }
            for fc in items
        ]
        if rows:
            sb.table("jira_field_configurations").insert(rows).execute()
        _log_sync("field_configurations", len(rows))
        return rows
    except Exception as e:
        _log_sync("field_configurations", 0, "error", str(e))
        raise


# ── Field Configuration Schemes ───────────────────────

async def sync_field_config_schemes():
    from .jira.configuration import get_all_field_config_schemes
    try:
        items = await get_all_field_config_schemes()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "scheme_id": s.scheme_id,
                "name": s.name,
                "description": s.description,
                "is_default": s.is_default,
                "mappings": s.mappings,
                "synced_at": now,
            }
            for s in items
        ]
        if rows:
            sb.table("jira_field_config_schemes").insert(rows).execute()
        _log_sync("field_config_schemes", len(rows))
        return rows
    except Exception as e:
        _log_sync("field_config_schemes", 0, "error", str(e))
        raise


# ── Project Categories ────────────────────────────────

async def sync_project_categories():
    from .jira.configuration import get_all_project_categories
    try:
        items = await get_all_project_categories()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "category_id": c.category_id,
                "name": c.name,
                "description": c.description,
                "project_count": c.project_count,
                "synced_at": now,
            }
            for c in items
        ]
        if rows:
            sb.table("jira_project_categories").insert(rows).execute()
        _log_sync("project_categories", len(rows))
        return rows
    except Exception as e:
        _log_sync("project_categories", 0, "error", str(e))
        raise


# ── Project Roles ─────────────────────────────────────

async def sync_project_roles():
    from .jira.configuration import get_all_project_roles
    try:
        items = await get_all_project_roles()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "role_id": r.role_id,
                "name": r.name,
                "description": r.description,
                "is_admin": r.is_admin,
                "synced_at": now,
            }
            for r in items
        ]
        if rows:
            sb.table("jira_project_roles").insert(rows).execute()
        _log_sync("project_roles", len(rows))
        return rows
    except Exception as e:
        _log_sync("project_roles", 0, "error", str(e))
        raise


# ── Groups ────────────────────────────────────────────

async def sync_groups():
    from .jira.groups import get_all_groups_with_members
    try:
        groups_data = await get_all_groups_with_members()
        sb = get_supabase()
        now = _now()

        group_rows = [
            {
                "group_id": g["group"]["group_id"],
                "name": g["group"]["name"],
                "member_count": g["member_count"],
                "synced_at": now,
            }
            for g in groups_data
        ]
        if group_rows:
            sb.table("jira_groups").insert(group_rows).execute()

        member_rows = []
        for g in groups_data:
            for m in g["members"]:
                member_rows.append({
                    "group_id": m["group_id"],
                    "group_name": m["group_name"],
                    "account_id": m["account_id"],
                    "display_name": m["display_name"],
                    "email": m["email"],
                    "active": m["active"],
                    "synced_at": now,
                })
        if member_rows:
            for i in range(0, len(member_rows), 500):
                sb.table("jira_group_members").insert(member_rows[i:i+500]).execute()

        total = len(group_rows) + len(member_rows)
        _log_sync("groups", total)
        return {"groups": len(group_rows), "members": len(member_rows)}
    except Exception as e:
        _log_sync("groups", 0, "error", str(e))
        raise


# ── Application Roles ─────────────────────────────────

async def sync_application_roles():
    from .jira.groups import get_application_roles
    try:
        items = await get_application_roles()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "role_key": r.role_key,
                "name": r.name,
                "user_count": r.user_count,
                "remaining_seats": r.remaining_seats,
                "groups": r.groups,
                "default_groups": r.default_groups,
                "has_unlimited_seats": r.has_unlimited_seats,
                "synced_at": now,
            }
            for r in items
        ]
        if rows:
            sb.table("jira_application_roles").insert(rows).execute()
        _log_sync("application_roles", len(rows))
        return rows
    except Exception as e:
        _log_sync("application_roles", 0, "error", str(e))
        raise


# ── Filters ───────────────────────────────────────────

async def sync_filters():
    from .jira.filters_dashboards import get_all_filters
    try:
        items = await get_all_filters()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "filter_id": f.filter_id,
                "name": f.name,
                "description": f.description,
                "owner_account_id": f.owner_account_id,
                "owner_display_name": f.owner_display_name,
                "jql": f.jql,
                "is_favourite": f.is_favourite,
                "favourite_count": f.favourite_count,
                "share_permissions": f.share_permissions,
                "subscriptions": f.subscriptions,
                "synced_at": now,
            }
            for f in items
        ]
        if rows:
            sb.table("jira_filters").insert(rows).execute()
        _log_sync("filters", len(rows))
        return rows
    except Exception as e:
        _log_sync("filters", 0, "error", str(e))
        raise


# ── Dashboards ────────────────────────────────────────

async def sync_dashboards():
    from .jira.filters_dashboards import get_all_dashboards
    try:
        items = await get_all_dashboards()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "dashboard_id": d.dashboard_id,
                "name": d.name,
                "description": d.description,
                "owner_account_id": d.owner_account_id,
                "owner_display_name": d.owner_display_name,
                "is_system": d.is_system,
                "is_favourite": d.is_favourite,
                "share_permissions": d.share_permissions,
                "gadgets": d.gadgets,
                "synced_at": now,
            }
            for d in items
        ]
        if rows:
            sb.table("jira_dashboards").insert(rows).execute()
        _log_sync("dashboards", len(rows))
        return rows
    except Exception as e:
        _log_sync("dashboards", 0, "error", str(e))
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
                "description": s.description,
                "homepage_id": s.homepage_id,
                "status": s.status,
                "total_pages": s.total_pages,
                "total_blog_posts": s.total_blog_posts,
                "total_attachments": s.total_attachments,
                "attachment_size_mb": s.attachment_size_mb,
                "active_contributors": s.active_contributors,
                "permissions_summary": s.permissions_summary,
                "labels": s.labels,
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


# ── Confluence Templates ──────────────────────────────

async def sync_confluence_templates():
    from .confluence.templates import get_all_templates
    try:
        items = await get_all_templates()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "template_id": t.template_id,
                "name": t.name,
                "description": t.description,
                "template_type": t.template_type,
                "space_key": t.space_key,
                "body_format": t.body_format,
                "labels": t.labels,
                "synced_at": now,
            }
            for t in items
        ]
        if rows:
            sb.table("confluence_templates").insert(rows).execute()
        _log_sync("confluence_templates", len(rows))
        return rows
    except Exception as e:
        _log_sync("confluence_templates", 0, "error", str(e))
        raise


# ── JSM Service Desks ────────────────────────────────

async def sync_jsm_service_desks():
    from .jsm.service_desks import get_all_service_desks, get_request_types, get_queues
    try:
        desks = await get_all_service_desks()
        sb = get_supabase()
        now = _now()

        desk_rows = [
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
        if desk_rows:
            sb.table("jsm_service_desks").insert(desk_rows).execute()

        rt_rows = []
        queue_rows = []
        for desk in desks:
            try:
                rts = await get_request_types(desk.service_desk_id)
                for rt in rts:
                    rt_rows.append({
                        "request_type_id": rt.request_type_id,
                        "name": rt.request_type_name,
                        "description": rt.description,
                        "help_text": rt.help_text,
                        "service_desk_id": rt.service_desk_id,
                        "icon_url": rt.icon_url,
                        "portal_id": rt.portal_id,
                        "group_ids": rt.group_ids,
                        "fields": rt.fields,
                        "synced_at": now,
                    })
            except Exception as e:
                logger.warning(f"Failed to sync request types for desk {desk.service_desk_id}: {e}")

            try:
                qs = await get_queues(desk.service_desk_id)
                for q in qs:
                    queue_rows.append({
                        "queue_id": q.queue_id,
                        "name": q.queue_name,
                        "service_desk_id": q.service_desk_id,
                        "jql": q.jql,
                        "issue_count": q.issue_count,
                        "synced_at": now,
                    })
            except Exception as e:
                logger.warning(f"Failed to sync queues for desk {desk.service_desk_id}: {e}")

        if rt_rows:
            sb.table("jsm_request_types").insert(rt_rows).execute()
        if queue_rows:
            sb.table("jsm_queues").insert(queue_rows).execute()

        total = len(desk_rows) + len(rt_rows) + len(queue_rows)
        _log_sync("jsm_service_desks", total)
        return {"desks": len(desk_rows), "request_types": len(rt_rows), "queues": len(queue_rows)}
    except Exception as e:
        _log_sync("jsm_service_desks", 0, "error", str(e))
        raise


# ── JSM Organizations ─────────────────────────────────

async def sync_jsm_organizations():
    from .jsm.organizations import get_all_organizations
    try:
        items = await get_all_organizations()
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "org_id": o.org_id,
                "name": o.name,
                "synced_at": now,
            }
            for o in items
        ]
        if rows:
            sb.table("jsm_organizations").insert(rows).execute()
        _log_sync("jsm_organizations", len(rows))
        return rows
    except Exception as e:
        _log_sync("jsm_organizations", 0, "error", str(e))
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
                "tier": lic.tier,
                "billable_users": lic.billable_users,
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


# ── Audit Log ─────────────────────────────────────────

async def sync_audit_log():
    from .jira.audit import get_audit_records
    try:
        items = await get_audit_records(limit=200)
        sb = get_supabase()
        now = _now()
        rows = [
            {
                "audit_id": a.audit_id,
                "summary": a.summary,
                "category": a.category,
                "event_source": a.event_source,
                "author_id": a.author_id,
                "author_name": a.author_name,
                "object_type": a.object_type,
                "object_name": a.object_name,
                "object_id": a.object_id,
                "created": a.created.isoformat() if a.created else None,
                "changed_values": a.changed_values,
                "associated_items": a.associated_items,
                "synced_at": now,
            }
            for a in items
        ]
        if rows:
            sb.table("audit_log").insert(rows).execute()
        _log_sync("audit_log", len(rows))
        return rows
    except Exception as e:
        _log_sync("audit_log", 0, "error", str(e))
        raise


# ── Instance Info ─────────────────────────────────────

async def sync_instance_info():
    from .jira.audit import get_instance_info
    try:
        info = await get_instance_info()
        sb = get_supabase()
        now = _now()
        row = {
            "base_url": info.base_url,
            "version": info.version,
            "build_number": info.build_number,
            "deployment_type": info.deployment_type,
            "scm_info": info.scm_info,
            "server_title": info.server_title,
            "default_locale": info.default_locale,
            "synced_at": now,
        }
        sb.table("instance_info").insert(row).execute()
        _log_sync("instance_info", 1)
        return row
    except Exception as e:
        _log_sync("instance_info", 0, "error", str(e))
        raise


# ── Dashboard Snapshot ────────────────────────────────

async def sync_dashboard_snapshot():
    """Save a point-in-time dashboard snapshot for trend analysis."""
    from .jira.projects import get_all_projects
    from .jira.custom_fields import get_all_custom_fields, get_unused_custom_fields
    from .jira.user_tracking import get_all_jira_users
    from .jira.workflows import get_all_workflows, get_all_schemes_summary
    from .jira.groups import get_all_groups
    from .jira.filters_dashboards import get_all_filters, get_all_dashboards
    from .confluence.spaces import get_all_spaces
    from .jsm.service_desks import get_all_service_desks

    try:
        (
            projects, spaces, desks, users, cfs, unused_cfs,
            workflows, groups, filters, dashboards
        ) = await asyncio.gather(
            get_all_projects(),
            get_all_spaces(),
            get_all_service_desks(),
            get_all_jira_users(),
            get_all_custom_fields(),
            get_unused_custom_fields(),
            get_all_workflows(),
            get_all_groups(),
            get_all_filters(),
            get_all_dashboards(),
        )

        schemes_summary = await get_all_schemes_summary()
        total_schemes = sum(
            v["count"] for v in schemes_summary.values()
            if isinstance(v, dict) and "count" in v
        )

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
            "total_workflows": len(workflows),
            "total_schemes": total_schemes,
            "total_groups": len(groups),
            "total_filters": len(filters),
            "total_dashboards_jira": len(dashboards),
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
    """Run all sync operations in phased order."""
    results = {}

    # Phase 1: Core configuration (fast, independent)
    phase1 = [
        ("instance_info", sync_instance_info),
        ("issue_types", sync_issue_types),
        ("statuses", sync_statuses),
        ("priorities", sync_priorities),
        ("resolutions", sync_resolutions),
        ("project_categories", sync_project_categories),
        ("project_roles", sync_project_roles),
        ("application_roles", sync_application_roles),
    ]

    # Phase 2: Main entities
    phase2 = [
        ("jira_users", sync_jira_users),
        ("custom_fields", sync_custom_fields),
        ("jira_projects", sync_jira_projects),
        ("workflows", sync_workflows),
        ("schemes", sync_schemes),
        ("screens", sync_screens),
        ("screen_schemes", sync_screen_schemes),
        ("issue_type_screen_schemes", sync_issue_type_screen_schemes),
        ("field_configurations", sync_field_configurations),
        ("field_config_schemes", sync_field_config_schemes),
        ("groups", sync_groups),
        ("filters", sync_filters),
        ("dashboards", sync_dashboards),
    ]

    # Phase 3: Cross-product
    phase3 = [
        ("confluence_spaces", sync_confluence_spaces),
        ("confluence_templates", sync_confluence_templates),
        ("jsm_service_desks", sync_jsm_service_desks),
        ("jsm_organizations", sync_jsm_organizations),
    ]

    # Phase 4: Governance & audit
    phase4 = [
        ("cleanup_recommendations", sync_cleanup_recommendations),
        ("permissions_audit", sync_permissions_audit),
        ("license_usage", sync_license_usage),
        ("audit_log", sync_audit_log),
    ]

    # Phase 5: Snapshot (depends on prior data)
    phase5 = [
        ("dashboard_snapshot", sync_dashboard_snapshot),
    ]

    for phase_name, phase in [
        ("configuration", phase1),
        ("entities", phase2),
        ("cross_product", phase3),
        ("governance", phase4),
        ("snapshot", phase5),
    ]:
        logger.info(f"Starting sync phase: {phase_name}")
        for name, fn in phase:
            try:
                results[name] = {"status": "success", "data": await fn()}
            except Exception as e:
                logger.error(f"Sync failed for {name}: {e}")
                results[name] = {"status": "error", "error": str(e)}

    return results
