-- ================================================================
-- Atlassian Admin Tracker — Comprehensive Schema Extension
-- Adds missing columns to existing tables and creates new tables
-- for full Atlassian API data capture
-- ================================================================

-- ┌─────────────────────────────────────────────────────────┐
-- │  ALTER EXISTING TABLES — add missing columns            │
-- └─────────────────────────────────────────────────────────┘

-- Jira Users: add profile details + last activity tracking
ALTER TABLE jira_users ADD COLUMN IF NOT EXISTS account_type TEXT DEFAULT 'atlassian';
ALTER TABLE jira_users ADD COLUMN IF NOT EXISTS avatar_url TEXT;
ALTER TABLE jira_users ADD COLUMN IF NOT EXISTS timezone TEXT;
ALTER TABLE jira_users ADD COLUMN IF NOT EXISTS locale TEXT;
ALTER TABLE jira_users ADD COLUMN IF NOT EXISTS last_active TIMESTAMPTZ;
ALTER TABLE jira_users ADD COLUMN IF NOT EXISTS groups JSONB DEFAULT '[]';

-- Jira Projects: add full project metadata + scheme associations
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS project_id TEXT;
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS category_id TEXT;
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS category_name TEXT;
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS url TEXT;
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS avatar_url TEXT;
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS simplified BOOLEAN DEFAULT false;
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS is_private BOOLEAN DEFAULT false;
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS style TEXT;
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS permission_scheme_id TEXT;
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS notification_scheme_id TEXT;
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS issue_type_scheme_id TEXT;
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS workflow_scheme_id TEXT;
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS field_config_scheme_id TEXT;
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS issue_type_screen_scheme_id TEXT;
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS components JSONB DEFAULT '[]';
ALTER TABLE jira_projects ADD COLUMN IF NOT EXISTS versions JSONB DEFAULT '[]';

-- Custom Fields: add richer field metadata
ALTER TABLE custom_fields ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE custom_fields ADD COLUMN IF NOT EXISTS searcher_key TEXT;
ALTER TABLE custom_fields ADD COLUMN IF NOT EXISTS schema_type TEXT;
ALTER TABLE custom_fields ADD COLUMN IF NOT EXISTS schema_custom TEXT;
ALTER TABLE custom_fields ADD COLUMN IF NOT EXISTS schema_custom_id BIGINT;
ALTER TABLE custom_fields ADD COLUMN IF NOT EXISTS context_project_ids JSONB DEFAULT '[]';
ALTER TABLE custom_fields ADD COLUMN IF NOT EXISTS is_locked BOOLEAN DEFAULT false;
ALTER TABLE custom_fields ADD COLUMN IF NOT EXISTS is_managed BOOLEAN DEFAULT false;

-- Schemes: add description + project mapping
ALTER TABLE schemes ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE schemes ADD COLUMN IF NOT EXISTS project_ids JSONB DEFAULT '[]';

-- Workflows: add description, scope, entity ID
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS workflow_id TEXT;
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS scope TEXT DEFAULT 'global';
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT false;
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS transition_details JSONB DEFAULT '[]';

-- Confluence Spaces: add full metadata
ALTER TABLE confluence_spaces ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE confluence_spaces ADD COLUMN IF NOT EXISTS homepage_id TEXT;
ALTER TABLE confluence_spaces ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'current';
ALTER TABLE confluence_spaces ADD COLUMN IF NOT EXISTS created_by TEXT;
ALTER TABLE confluence_spaces ADD COLUMN IF NOT EXISTS created_date TIMESTAMPTZ;
ALTER TABLE confluence_spaces ADD COLUMN IF NOT EXISTS permissions_summary JSONB DEFAULT '{}';
ALTER TABLE confluence_spaces ADD COLUMN IF NOT EXISTS labels JSONB DEFAULT '[]';

-- Confluence Content: add dates, hierarchy, engagement
ALTER TABLE confluence_content ADD COLUMN IF NOT EXISTS created_date TIMESTAMPTZ;
ALTER TABLE confluence_content ADD COLUMN IF NOT EXISTS last_updated TIMESTAMPTZ;
ALTER TABLE confluence_content ADD COLUMN IF NOT EXISTS last_updated_by TEXT;
ALTER TABLE confluence_content ADD COLUMN IF NOT EXISTS body_length INTEGER DEFAULT 0;
ALTER TABLE confluence_content ADD COLUMN IF NOT EXISTS ancestors JSONB DEFAULT '[]';
ALTER TABLE confluence_content ADD COLUMN IF NOT EXISTS comments_count INTEGER DEFAULT 0;
ALTER TABLE confluence_content ADD COLUMN IF NOT EXISTS child_count INTEGER DEFAULT 0;
ALTER TABLE confluence_content ADD COLUMN IF NOT EXISTS restrictions JSONB DEFAULT '{}';

-- JSM Service Desks: add portal and SLA info
ALTER TABLE jsm_service_desks ADD COLUMN IF NOT EXISTS portal_enabled BOOLEAN DEFAULT true;
ALTER TABLE jsm_service_desks ADD COLUMN IF NOT EXISTS portal_name TEXT;

-- License Usage: add billable flag and tier
ALTER TABLE license_usage ADD COLUMN IF NOT EXISTS tier TEXT;
ALTER TABLE license_usage ADD COLUMN IF NOT EXISTS billable_users INTEGER DEFAULT 0;

-- Dashboard Snapshots: add more metrics
ALTER TABLE dashboard_snapshots ADD COLUMN IF NOT EXISTS total_workflows INTEGER DEFAULT 0;
ALTER TABLE dashboard_snapshots ADD COLUMN IF NOT EXISTS total_schemes INTEGER DEFAULT 0;
ALTER TABLE dashboard_snapshots ADD COLUMN IF NOT EXISTS total_groups INTEGER DEFAULT 0;
ALTER TABLE dashboard_snapshots ADD COLUMN IF NOT EXISTS total_filters INTEGER DEFAULT 0;
ALTER TABLE dashboard_snapshots ADD COLUMN IF NOT EXISTS total_dashboards_jira INTEGER DEFAULT 0;


-- ┌─────────────────────────────────────────────────────────┐
-- │  NEW TABLES — Jira Configuration Entities               │
-- └─────────────────────────────────────────────────────────┘

-- Issue Types (Bug, Story, Task, Epic, Sub-task, etc.)
CREATE TABLE IF NOT EXISTS jira_issue_types (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    issue_type_id   TEXT NOT NULL,
    name            TEXT NOT NULL,
    description     TEXT,
    icon_url        TEXT,
    subtask         BOOLEAN NOT NULL DEFAULT false,
    hierarchy_level INTEGER DEFAULT 0,
    scope           TEXT DEFAULT 'global',          -- global | project:{key}
    avatar_id       TEXT,
    synced_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(issue_type_id, synced_at)
);

-- Statuses (To Do, In Progress, Done, etc.)
CREATE TABLE IF NOT EXISTS jira_statuses (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    status_id         TEXT NOT NULL,
    name              TEXT NOT NULL,
    description       TEXT,
    status_category   TEXT NOT NULL DEFAULT 'undefined',  -- new | indeterminate | done | undefined
    status_category_id TEXT,
    scope             TEXT DEFAULT 'global',               -- global | project:{key}
    usages            INTEGER DEFAULT 0,                   -- number of workflows using this status
    synced_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(status_id, synced_at)
);

-- Priorities
CREATE TABLE IF NOT EXISTS jira_priorities (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    priority_id   TEXT NOT NULL,
    name          TEXT NOT NULL,
    description   TEXT,
    icon_url      TEXT,
    status_color  TEXT,
    is_default    BOOLEAN DEFAULT false,
    sort_order    INTEGER DEFAULT 0,
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(priority_id, synced_at)
);

-- Resolutions
CREATE TABLE IF NOT EXISTS jira_resolutions (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    resolution_id   TEXT NOT NULL,
    name            TEXT NOT NULL,
    description     TEXT,
    is_default      BOOLEAN DEFAULT false,
    synced_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(resolution_id, synced_at)
);

-- Screens
CREATE TABLE IF NOT EXISTS jira_screens (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    screen_id     TEXT NOT NULL,
    name          TEXT NOT NULL,
    description   TEXT,
    scope         TEXT DEFAULT 'global',
    tab_count     INTEGER DEFAULT 0,
    tabs          JSONB DEFAULT '[]',               -- [{id, name, fields: [...]}]
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(screen_id, synced_at)
);

-- Screen Schemes
CREATE TABLE IF NOT EXISTS jira_screen_schemes (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    scheme_id     TEXT NOT NULL,
    name          TEXT NOT NULL,
    description   TEXT,
    screens       JSONB DEFAULT '{}',               -- {create: screen_id, edit: screen_id, view: screen_id, default: screen_id}
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(scheme_id, synced_at)
);

-- Issue Type Screen Schemes
CREATE TABLE IF NOT EXISTS jira_issue_type_screen_schemes (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    scheme_id     TEXT NOT NULL,
    name          TEXT NOT NULL,
    description   TEXT,
    mappings      JSONB DEFAULT '[]',               -- [{issueTypeId, screenSchemeId}]
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(scheme_id, synced_at)
);

-- Field Configurations
CREATE TABLE IF NOT EXISTS jira_field_configurations (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    config_id     TEXT NOT NULL,
    name          TEXT NOT NULL,
    description   TEXT,
    is_default    BOOLEAN DEFAULT false,
    fields        JSONB DEFAULT '[]',               -- [{id, description, isHidden, isRequired}]
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(config_id, synced_at)
);

-- Field Configuration Schemes
CREATE TABLE IF NOT EXISTS jira_field_config_schemes (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    scheme_id     TEXT NOT NULL,
    name          TEXT NOT NULL,
    description   TEXT,
    is_default    BOOLEAN DEFAULT false,
    mappings      JSONB DEFAULT '[]',               -- [{issueTypeId, fieldConfigurationId}]
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(scheme_id, synced_at)
);

-- Project Categories
CREATE TABLE IF NOT EXISTS jira_project_categories (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_id   TEXT NOT NULL,
    name          TEXT NOT NULL,
    description   TEXT,
    project_count INTEGER DEFAULT 0,
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(category_id, synced_at)
);

-- Project Roles
CREATE TABLE IF NOT EXISTS jira_project_roles (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    role_id       TEXT NOT NULL,
    name          TEXT NOT NULL,
    description   TEXT,
    is_admin      BOOLEAN DEFAULT false,
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(role_id, synced_at)
);

-- Project Role Actors (who has which role in which project)
CREATE TABLE IF NOT EXISTS jira_project_role_actors (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_key   TEXT NOT NULL,
    role_id       TEXT NOT NULL,
    role_name     TEXT NOT NULL,
    actor_type    TEXT NOT NULL,                     -- atlassian-user-role-actor | atlassian-group-role-actor
    actor_name    TEXT NOT NULL,                     -- display_name or group_name
    actor_id      TEXT,                              -- account_id or group_id
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- ┌─────────────────────────────────────────────────────────┐
-- │  NEW TABLES — User & Group Management                   │
-- └─────────────────────────────────────────────────────────┘

-- Groups
CREATE TABLE IF NOT EXISTS jira_groups (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    group_id      TEXT NOT NULL,
    name          TEXT NOT NULL,
    member_count  INTEGER DEFAULT 0,
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(group_id, synced_at)
);

-- Group Members
CREATE TABLE IF NOT EXISTS jira_group_members (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    group_id      TEXT NOT NULL,
    group_name    TEXT NOT NULL,
    account_id    TEXT NOT NULL,
    display_name  TEXT,
    email         TEXT,
    active        BOOLEAN DEFAULT true,
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Application Roles (product access)
CREATE TABLE IF NOT EXISTS jira_application_roles (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    role_key      TEXT NOT NULL,                     -- e.g. jira-software, jira-servicedesk, confluence
    name          TEXT NOT NULL,
    user_count    INTEGER DEFAULT 0,
    remaining_seats INTEGER,
    groups        JSONB DEFAULT '[]',
    default_groups JSONB DEFAULT '[]',
    has_unlimited_seats BOOLEAN DEFAULT false,
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(role_key, synced_at)
);


-- ┌─────────────────────────────────────────────────────────┐
-- │  NEW TABLES — Saved Artifacts (Filters & Dashboards)    │
-- └─────────────────────────────────────────────────────────┘

-- Saved Filters
CREATE TABLE IF NOT EXISTS jira_filters (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    filter_id         TEXT NOT NULL,
    name              TEXT NOT NULL,
    description       TEXT,
    owner_account_id  TEXT,
    owner_display_name TEXT,
    jql               TEXT,
    is_favourite      BOOLEAN DEFAULT false,
    favourite_count   INTEGER DEFAULT 0,
    share_permissions JSONB DEFAULT '[]',            -- [{type: "project"|"group"|"global", ...}]
    subscriptions     JSONB DEFAULT '[]',
    synced_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(filter_id, synced_at)
);

-- Jira Dashboards
CREATE TABLE IF NOT EXISTS jira_dashboards (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dashboard_id        TEXT NOT NULL,
    name                TEXT NOT NULL,
    description         TEXT,
    owner_account_id    TEXT,
    owner_display_name  TEXT,
    is_system           BOOLEAN DEFAULT false,
    is_favourite        BOOLEAN DEFAULT false,
    share_permissions   JSONB DEFAULT '[]',
    gadgets             JSONB DEFAULT '[]',          -- [{id, title, module_key, ...}]
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(dashboard_id, synced_at)
);


-- ┌─────────────────────────────────────────────────────────┐
-- │  NEW TABLES — JSM Extended Entities                     │
-- └─────────────────────────────────────────────────────────┘

-- JSM Request Types (per service desk)
CREATE TABLE IF NOT EXISTS jsm_request_types (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_type_id   TEXT NOT NULL,
    name              TEXT NOT NULL,
    description       TEXT,
    help_text         TEXT,
    service_desk_id   TEXT NOT NULL,
    icon_url          TEXT,
    portal_id         TEXT,
    group_ids         JSONB DEFAULT '[]',
    fields            JSONB DEFAULT '[]',            -- [{fieldId, name, required, ...}]
    synced_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(request_type_id, service_desk_id, synced_at)
);

-- JSM Queues (per service desk)
CREATE TABLE IF NOT EXISTS jsm_queues (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    queue_id        TEXT NOT NULL,
    name            TEXT NOT NULL,
    service_desk_id TEXT NOT NULL,
    jql             TEXT,
    issue_count     INTEGER DEFAULT 0,
    synced_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(queue_id, service_desk_id, synced_at)
);

-- JSM SLA Metrics
CREATE TABLE IF NOT EXISTS jsm_sla_metrics (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sla_name            TEXT NOT NULL,
    service_desk_id     TEXT NOT NULL,
    completed_on_time   INTEGER DEFAULT 0,
    completed_late      INTEGER DEFAULT 0,
    in_progress         INTEGER DEFAULT 0,
    compliance_pct      REAL DEFAULT 0.0,
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- JSM Organizations
CREATE TABLE IF NOT EXISTS jsm_organizations (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    org_id        TEXT NOT NULL,
    name          TEXT NOT NULL,
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(org_id, synced_at)
);


-- ┌─────────────────────────────────────────────────────────┐
-- │  NEW TABLES — Confluence Extended                       │
-- └─────────────────────────────────────────────────────────┘

-- Confluence Templates
CREATE TABLE IF NOT EXISTS confluence_templates (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    template_id   TEXT NOT NULL,
    name          TEXT NOT NULL,
    description   TEXT,
    template_type TEXT DEFAULT 'page',               -- page | blogpost
    space_key     TEXT,                               -- NULL = global template
    body_format   TEXT DEFAULT 'storage',
    labels        JSONB DEFAULT '[]',
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Confluence Space Permissions (normalized from space data)
CREATE TABLE IF NOT EXISTS confluence_space_permissions (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    space_key       TEXT NOT NULL,
    principal_type  TEXT NOT NULL,                    -- user | group
    principal_name  TEXT NOT NULL,
    principal_id    TEXT,
    operations      JSONB DEFAULT '[]',              -- ["read", "write", "administer", ...]
    synced_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- ┌─────────────────────────────────────────────────────────┐
-- │  NEW TABLES — Audit & Platform                          │
-- └─────────────────────────────────────────────────────────┘

-- Audit Log entries (from /rest/api/3/auditing/record)
CREATE TABLE IF NOT EXISTS audit_log (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    audit_id        TEXT,
    summary         TEXT NOT NULL,
    category        TEXT,                            -- e.g. "user management", "permissions", "project"
    event_source    TEXT,
    author_id       TEXT,
    author_name     TEXT,
    object_type     TEXT,                            -- e.g. "USER", "PROJECT", "PERMISSION_SCHEME"
    object_name     TEXT,
    object_id       TEXT,
    created         TIMESTAMPTZ,
    changed_values  JSONB DEFAULT '[]',              -- [{fieldName, changedFrom, changedTo}]
    associated_items JSONB DEFAULT '[]',
    synced_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Server / Instance Info
CREATE TABLE IF NOT EXISTS instance_info (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    base_url        TEXT NOT NULL,
    version         TEXT,
    build_number    TEXT,
    deployment_type TEXT DEFAULT 'Cloud',
    scm_info        TEXT,
    server_title    TEXT,
    default_locale  TEXT,
    synced_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- ┌─────────────────────────────────────────────────────────┐
-- │  INDEXES for new tables                                 │
-- └─────────────────────────────────────────────────────────┘

CREATE INDEX IF NOT EXISTS idx_issue_types_synced ON jira_issue_types(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_statuses_synced ON jira_statuses(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_priorities_synced ON jira_priorities(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_resolutions_synced ON jira_resolutions(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_screens_synced ON jira_screens(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_screen_schemes_synced ON jira_screen_schemes(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_itss_synced ON jira_issue_type_screen_schemes(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_field_configs_synced ON jira_field_configurations(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_field_config_schemes_synced ON jira_field_config_schemes(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_project_categories_synced ON jira_project_categories(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_project_roles_synced ON jira_project_roles(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_role_actors_project ON jira_project_role_actors(project_key, synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_groups_synced ON jira_groups(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_group_members_group ON jira_group_members(group_id, synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_app_roles_synced ON jira_application_roles(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_filters_synced ON jira_filters(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_filters_owner ON jira_filters(owner_account_id);
CREATE INDEX IF NOT EXISTS idx_dashboards_synced ON jira_dashboards(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_dashboards_owner ON jira_dashboards(owner_account_id);
CREATE INDEX IF NOT EXISTS idx_jsm_rt_desk ON jsm_request_types(service_desk_id, synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_jsm_queues_desk ON jsm_queues(service_desk_id, synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_jsm_sla_desk ON jsm_sla_metrics(service_desk_id, synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_jsm_orgs_synced ON jsm_organizations(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_confluence_templates_space ON confluence_templates(space_key);
CREATE INDEX IF NOT EXISTS idx_confluence_space_perms ON confluence_space_permissions(space_key, synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_created ON audit_log(created DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_category ON audit_log(category, created DESC);
CREATE INDEX IF NOT EXISTS idx_instance_info_synced ON instance_info(synced_at DESC);

-- Indexes on new columns in existing tables
CREATE INDEX IF NOT EXISTS idx_jira_projects_category ON jira_projects(category_id);
CREATE INDEX IF NOT EXISTS idx_jira_users_account_type ON jira_users(account_type);
CREATE INDEX IF NOT EXISTS idx_jira_users_last_active ON jira_users(last_active DESC);


-- ┌─────────────────────────────────────────────────────────┐
-- │  RLS on all new tables                                  │
-- └─────────────────────────────────────────────────────────┘

ALTER TABLE jira_issue_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_statuses ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_priorities ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_resolutions ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_screens ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_screen_schemes ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_issue_type_screen_schemes ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_field_configurations ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_field_config_schemes ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_project_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_project_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_project_role_actors ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_group_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_application_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_filters ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_dashboards ENABLE ROW LEVEL SECURITY;
ALTER TABLE jsm_request_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE jsm_queues ENABLE ROW LEVEL SECURITY;
ALTER TABLE jsm_sla_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE jsm_organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE confluence_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE confluence_space_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE instance_info ENABLE ROW LEVEL SECURITY;

-- Anon read policies
CREATE POLICY "anon_read" ON jira_issue_types FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_statuses FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_priorities FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_resolutions FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_screens FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_screen_schemes FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_issue_type_screen_schemes FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_field_configurations FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_field_config_schemes FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_project_categories FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_project_roles FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_project_role_actors FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_groups FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_group_members FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_application_roles FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_filters FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_dashboards FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jsm_request_types FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jsm_queues FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jsm_sla_metrics FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jsm_organizations FOR SELECT USING (true);
CREATE POLICY "anon_read" ON confluence_templates FOR SELECT USING (true);
CREATE POLICY "anon_read" ON confluence_space_permissions FOR SELECT USING (true);
CREATE POLICY "anon_read" ON audit_log FOR SELECT USING (true);
CREATE POLICY "anon_read" ON instance_info FOR SELECT USING (true);
