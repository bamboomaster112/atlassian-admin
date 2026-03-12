from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ── Jira ──────────────────────────────────────────────

class UserActivity(BaseModel):
    account_id: str
    display_name: str
    email: Optional[str] = None
    active: bool = True
    account_type: str = "atlassian"
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None
    last_active: Optional[datetime] = None
    issues_created: int = 0
    issues_resolved: int = 0
    issues_updated: int = 0
    comments_count: int = 0
    groups: list[str] = []
    product: str = "jira"


class CustomFieldUsage(BaseModel):
    field_id: str
    field_name: str
    field_type: str
    description: Optional[str] = None
    searcher_key: Optional[str] = None
    schema_type: Optional[str] = None
    schema_custom: Optional[str] = None
    schema_custom_id: Optional[int] = None
    projects_using: int = 0
    issues_using: int = 0
    screens_using: int = 0
    is_required: bool = False
    is_locked: bool = False
    is_managed: bool = False
    context_project_ids: list[str] = []
    last_used: Optional[datetime] = None
    recommendation: Optional[str] = None


class ProjectSummary(BaseModel):
    project_id: Optional[str] = None
    project_key: str
    project_name: str
    project_type: str
    description: Optional[str] = None
    lead: Optional[str] = None
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    url: Optional[str] = None
    avatar_url: Optional[str] = None
    simplified: bool = False
    is_private: bool = False
    style: Optional[str] = None
    issue_count: int = 0
    active_users: int = 0
    last_issue_created: Optional[datetime] = None
    permission_scheme_id: Optional[str] = None
    notification_scheme_id: Optional[str] = None
    issue_type_scheme_id: Optional[str] = None
    workflow_scheme_id: Optional[str] = None
    field_config_scheme_id: Optional[str] = None
    issue_type_screen_scheme_id: Optional[str] = None
    components: list[dict] = []
    versions: list[dict] = []
    workflows: list[str] = []
    schemes: dict = {}


class WorkflowUsage(BaseModel):
    workflow_name: str
    workflow_id: Optional[str] = None
    description: Optional[str] = None
    scope: str = "global"
    projects_using: int = 0
    statuses: list[str] = []
    transitions: int = 0
    transition_details: list[dict] = []
    is_default: bool = False


class SchemeUsage(BaseModel):
    scheme_name: str
    scheme_type: str
    scheme_id: str
    description: Optional[str] = None
    projects_using: int = 0
    project_ids: list[str] = []
    is_default: bool = False


class IssueType(BaseModel):
    issue_type_id: str
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    subtask: bool = False
    hierarchy_level: int = 0
    scope: str = "global"
    avatar_id: Optional[str] = None


class JiraStatus(BaseModel):
    status_id: str
    name: str
    description: Optional[str] = None
    status_category: str = "undefined"
    status_category_id: Optional[str] = None
    scope: str = "global"
    usages: int = 0


class JiraPriority(BaseModel):
    priority_id: str
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    status_color: Optional[str] = None
    is_default: bool = False
    sort_order: int = 0


class JiraResolution(BaseModel):
    resolution_id: str
    name: str
    description: Optional[str] = None
    is_default: bool = False


class JiraScreen(BaseModel):
    screen_id: str
    name: str
    description: Optional[str] = None
    scope: str = "global"
    tab_count: int = 0
    tabs: list[dict] = []


class JiraScreenScheme(BaseModel):
    scheme_id: str
    name: str
    description: Optional[str] = None
    screens: dict = {}


class IssueTypeScreenScheme(BaseModel):
    scheme_id: str
    name: str
    description: Optional[str] = None
    mappings: list[dict] = []


class FieldConfiguration(BaseModel):
    config_id: str
    name: str
    description: Optional[str] = None
    is_default: bool = False
    fields: list[dict] = []


class FieldConfigScheme(BaseModel):
    scheme_id: str
    name: str
    description: Optional[str] = None
    is_default: bool = False
    mappings: list[dict] = []


class ProjectCategory(BaseModel):
    category_id: str
    name: str
    description: Optional[str] = None
    project_count: int = 0


class ProjectRole(BaseModel):
    role_id: str
    name: str
    description: Optional[str] = None
    is_admin: bool = False


class ProjectRoleActor(BaseModel):
    project_key: str
    role_id: str
    role_name: str
    actor_type: str
    actor_name: str
    actor_id: Optional[str] = None


class JiraGroup(BaseModel):
    group_id: str
    name: str
    member_count: int = 0


class GroupMember(BaseModel):
    group_id: str
    group_name: str
    account_id: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    active: bool = True


class ApplicationRole(BaseModel):
    role_key: str
    name: str
    user_count: int = 0
    remaining_seats: Optional[int] = None
    groups: list[str] = []
    default_groups: list[str] = []
    has_unlimited_seats: bool = False


class JiraFilter(BaseModel):
    filter_id: str
    name: str
    description: Optional[str] = None
    owner_account_id: Optional[str] = None
    owner_display_name: Optional[str] = None
    jql: Optional[str] = None
    is_favourite: bool = False
    favourite_count: int = 0
    share_permissions: list[dict] = []
    subscriptions: list[dict] = []


class JiraDashboard(BaseModel):
    dashboard_id: str
    name: str
    description: Optional[str] = None
    owner_account_id: Optional[str] = None
    owner_display_name: Optional[str] = None
    is_system: bool = False
    is_favourite: bool = False
    share_permissions: list[dict] = []
    gadgets: list[dict] = []


# ── Confluence ────────────────────────────────────────

class SpaceAnalytics(BaseModel):
    space_key: str
    space_name: str
    space_type: str
    description: Optional[str] = None
    homepage_id: Optional[str] = None
    status: str = "current"
    created_by: Optional[str] = None
    created_date: Optional[datetime] = None
    total_pages: int = 0
    total_blog_posts: int = 0
    total_attachments: int = 0
    attachment_size_mb: float = 0.0
    active_contributors: int = 0
    last_updated: Optional[datetime] = None
    permissions_summary: dict = {}
    labels: list[str] = []


class ContentAnalytics(BaseModel):
    content_id: str
    title: str
    space_key: str
    content_type: str
    created_by: Optional[str] = None
    created_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    last_updated_by: Optional[str] = None
    version: int = 1
    views: int = 0
    body_length: int = 0
    child_pages: int = 0
    comments_count: int = 0
    child_count: int = 0
    labels: list[str] = []
    ancestors: list[dict] = []
    restrictions: dict = {}


class ConfluenceTemplate(BaseModel):
    template_id: str
    name: str
    description: Optional[str] = None
    template_type: str = "page"
    space_key: Optional[str] = None
    body_format: str = "storage"
    labels: list[str] = []


class SpacePermission(BaseModel):
    space_key: str
    principal_type: str
    principal_name: str
    principal_id: Optional[str] = None
    operations: list[str] = []


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
    portal_enabled: bool = True
    portal_name: Optional[str] = None


class RequestTypeUsage(BaseModel):
    request_type_id: str
    request_type_name: str
    service_desk_id: str
    description: Optional[str] = None
    help_text: Optional[str] = None
    icon_url: Optional[str] = None
    portal_id: Optional[str] = None
    group_ids: list[str] = []
    requests_count: int = 0
    avg_resolution_hours: Optional[float] = None
    fields: list[dict] = []


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


class JSMOrganization(BaseModel):
    org_id: str
    name: str


# ── Governance / Cross-product ────────────────────────

class LicenseUsage(BaseModel):
    product: str
    total_licenses: Optional[int] = None
    active_users: int = 0
    inactive_users: int = 0
    tier: Optional[str] = None
    billable_users: int = 0
    last_synced: Optional[datetime] = None


class PermissionAuditEntry(BaseModel):
    entity_type: str
    entity_name: str
    product: str
    scope: str
    scope_key: Optional[str] = None
    permissions: list[str] = []


class CleanupRecommendation(BaseModel):
    category: str
    item_name: str
    item_id: str
    reason: str
    impact: str
    product: str


class AuditLogEntry(BaseModel):
    audit_id: Optional[str] = None
    summary: str
    category: Optional[str] = None
    event_source: Optional[str] = None
    author_id: Optional[str] = None
    author_name: Optional[str] = None
    object_type: Optional[str] = None
    object_name: Optional[str] = None
    object_id: Optional[str] = None
    created: Optional[datetime] = None
    changed_values: list[dict] = []
    associated_items: list[dict] = []


class InstanceInfo(BaseModel):
    base_url: str
    version: Optional[str] = None
    build_number: Optional[str] = None
    deployment_type: str = "Cloud"
    scm_info: Optional[str] = None
    server_title: Optional[str] = None
    default_locale: Optional[str] = None


class AdminDashboard(BaseModel):
    jira_projects: int = 0
    confluence_spaces: int = 0
    jsm_service_desks: int = 0
    total_users: int = 0
    active_users: int = 0
    inactive_users: int = 0
    custom_fields_total: int = 0
    custom_fields_unused: int = 0
    total_workflows: int = 0
    total_schemes: int = 0
    total_groups: int = 0
    total_filters: int = 0
    total_dashboards_jira: int = 0
    cleanup_recommendations: int = 0
    last_synced: Optional[datetime] = None
