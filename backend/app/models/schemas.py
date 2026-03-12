from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ── Jira ──────────────────────────────────────────────

class UserActivity(BaseModel):
    account_id: str
    display_name: str
    email: Optional[str] = None
    active: bool = True
    last_active: Optional[datetime] = None
    issues_created: int = 0
    issues_resolved: int = 0
    issues_updated: int = 0
    comments_count: int = 0
    product: str = "jira"  # jira | confluence | jsm


class CustomFieldUsage(BaseModel):
    field_id: str
    field_name: str
    field_type: str
    projects_using: int = 0
    issues_using: int = 0
    screens_using: int = 0
    is_required: bool = False
    last_used: Optional[datetime] = None
    recommendation: Optional[str] = None


class ProjectSummary(BaseModel):
    project_key: str
    project_name: str
    project_type: str
    lead: Optional[str] = None
    issue_count: int = 0
    active_users: int = 0
    last_issue_created: Optional[datetime] = None
    workflows: list[str] = []
    schemes: dict = {}


class WorkflowUsage(BaseModel):
    workflow_name: str
    workflow_id: Optional[str] = None
    projects_using: int = 0
    statuses: list[str] = []
    transitions: int = 0


class SchemeUsage(BaseModel):
    scheme_name: str
    scheme_type: str  # permission | notification | issue_type | workflow | field_config
    scheme_id: str
    projects_using: int = 0
    is_default: bool = False


# ── Confluence ────────────────────────────────────────

class SpaceAnalytics(BaseModel):
    space_key: str
    space_name: str
    space_type: str
    total_pages: int = 0
    total_blog_posts: int = 0
    total_attachments: int = 0
    attachment_size_mb: float = 0.0
    active_contributors: int = 0
    last_updated: Optional[datetime] = None
    permissions_summary: dict = {}


class ContentAnalytics(BaseModel):
    content_id: str
    title: str
    space_key: str
    content_type: str  # page | blogpost
    created_by: Optional[str] = None
    created_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    version: int = 1
    views: int = 0
    child_pages: int = 0
    comments: int = 0
    labels: list[str] = []


class MacroUsage(BaseModel):
    macro_name: str
    pages_using: int = 0
    spaces_using: int = 0


# ── JSM ───────────────────────────────────────────────

class ServiceDeskSummary(BaseModel):
    service_desk_id: str
    service_desk_name: str
    project_key: str
    request_types: int = 0
    queues: int = 0
    open_requests: int = 0
    avg_resolution_hours: Optional[float] = None
    sla_compliance_pct: Optional[float] = None
    agents: int = 0
    customers: int = 0


class RequestTypeUsage(BaseModel):
    request_type_id: str
    request_type_name: str
    service_desk_id: str
    requests_count: int = 0
    avg_resolution_hours: Optional[float] = None
    fields: list[str] = []


class SLAMetrics(BaseModel):
    sla_name: str
    service_desk_id: str
    completed_on_time: int = 0
    completed_late: int = 0
    in_progress: int = 0
    compliance_pct: float = 0.0


class QueueMetrics(BaseModel):
    queue_id: str
    queue_name: str
    service_desk_id: str
    issue_count: int = 0
    jql: Optional[str] = None


# ── Governance / Cross-product ────────────────────────

class LicenseUsage(BaseModel):
    product: str
    total_licenses: Optional[int] = None
    active_users: int = 0
    inactive_users: int = 0
    last_synced: Optional[datetime] = None


class PermissionAuditEntry(BaseModel):
    entity_type: str  # user | group
    entity_name: str
    product: str
    scope: str  # global | project | space
    scope_key: Optional[str] = None
    permissions: list[str] = []


class CleanupRecommendation(BaseModel):
    category: str  # custom_field | workflow | scheme | space | project | user
    item_name: str
    item_id: str
    reason: str
    impact: str  # low | medium | high
    product: str


class AdminDashboard(BaseModel):
    """Top-level dashboard response."""
    jira_projects: int = 0
    confluence_spaces: int = 0
    jsm_service_desks: int = 0
    total_users: int = 0
    active_users: int = 0
    inactive_users: int = 0
    custom_fields_total: int = 0
    custom_fields_unused: int = 0
    cleanup_recommendations: int = 0
    last_synced: Optional[datetime] = None
