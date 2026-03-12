-- ================================================================
-- Atlassian Admin Tracker — Supabase schema
-- Run this in Supabase SQL Editor (Dashboard > SQL Editor > New Query)
-- ================================================================

-- Sync history: tracks when each data category was last synced
CREATE TABLE IF NOT EXISTS sync_history (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category      TEXT NOT NULL,          -- e.g. 'jira_users', 'custom_fields', 'confluence_spaces'
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    record_count  INTEGER NOT NULL DEFAULT 0,
    status        TEXT NOT NULL DEFAULT 'success',  -- success | error
    error_message TEXT
);

-- Jira users snapshot
CREATE TABLE IF NOT EXISTS jira_users (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    account_id    TEXT NOT NULL,
    display_name  TEXT NOT NULL DEFAULT '',
    email         TEXT,
    active        BOOLEAN NOT NULL DEFAULT true,
    issues_created  INTEGER NOT NULL DEFAULT 0,
    issues_resolved INTEGER NOT NULL DEFAULT 0,
    issues_updated  INTEGER NOT NULL DEFAULT 0,
    comments_count  INTEGER NOT NULL DEFAULT 0,
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(account_id, synced_at)
);

-- Custom fields
CREATE TABLE IF NOT EXISTS custom_fields (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    field_id       TEXT NOT NULL,
    field_name     TEXT NOT NULL DEFAULT '',
    field_type     TEXT NOT NULL DEFAULT 'unknown',
    projects_using INTEGER NOT NULL DEFAULT 0,
    issues_using   INTEGER NOT NULL DEFAULT 0,
    screens_using  INTEGER NOT NULL DEFAULT 0,
    is_required    BOOLEAN NOT NULL DEFAULT false,
    recommendation TEXT,
    synced_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(field_id, synced_at)
);

-- Jira projects
CREATE TABLE IF NOT EXISTS jira_projects (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_key     TEXT NOT NULL,
    project_name    TEXT NOT NULL DEFAULT '',
    project_type    TEXT NOT NULL DEFAULT '',
    lead            TEXT,
    issue_count     INTEGER NOT NULL DEFAULT 0,
    active_users    INTEGER NOT NULL DEFAULT 0,
    last_issue_created TIMESTAMPTZ,
    synced_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(project_key, synced_at)
);

-- Workflows
CREATE TABLE IF NOT EXISTS workflows (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    workflow_name   TEXT NOT NULL,
    projects_using  INTEGER NOT NULL DEFAULT 0,
    statuses        JSONB NOT NULL DEFAULT '[]',
    transitions     INTEGER NOT NULL DEFAULT 0,
    synced_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Schemes (all types)
CREATE TABLE IF NOT EXISTS schemes (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    scheme_name     TEXT NOT NULL,
    scheme_type     TEXT NOT NULL,    -- permission | notification | issue_type | workflow | field_config
    scheme_id       TEXT NOT NULL,
    projects_using  INTEGER NOT NULL DEFAULT 0,
    is_default      BOOLEAN NOT NULL DEFAULT false,
    synced_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Confluence spaces
CREATE TABLE IF NOT EXISTS confluence_spaces (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    space_key         TEXT NOT NULL,
    space_name        TEXT NOT NULL DEFAULT '',
    space_type        TEXT NOT NULL DEFAULT 'global',
    total_pages       INTEGER NOT NULL DEFAULT 0,
    total_blog_posts  INTEGER NOT NULL DEFAULT 0,
    total_attachments INTEGER NOT NULL DEFAULT 0,
    attachment_size_mb REAL NOT NULL DEFAULT 0.0,
    active_contributors INTEGER NOT NULL DEFAULT 0,
    synced_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(space_key, synced_at)
);

-- Confluence content analytics
CREATE TABLE IF NOT EXISTS confluence_content (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    content_id     TEXT NOT NULL,
    title          TEXT NOT NULL DEFAULT '',
    space_key      TEXT NOT NULL DEFAULT '',
    content_type   TEXT NOT NULL DEFAULT 'page',
    created_by     TEXT,
    version        INTEGER NOT NULL DEFAULT 1,
    views          INTEGER NOT NULL DEFAULT 0,
    labels         JSONB NOT NULL DEFAULT '[]',
    synced_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- JSM service desks
CREATE TABLE IF NOT EXISTS jsm_service_desks (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    service_desk_id     TEXT NOT NULL,
    service_desk_name   TEXT NOT NULL DEFAULT '',
    project_key         TEXT NOT NULL DEFAULT '',
    request_types       INTEGER NOT NULL DEFAULT 0,
    queues              INTEGER NOT NULL DEFAULT 0,
    open_requests       INTEGER NOT NULL DEFAULT 0,
    avg_resolution_hours REAL,
    sla_compliance_pct   REAL,
    agents              INTEGER NOT NULL DEFAULT 0,
    customers           INTEGER NOT NULL DEFAULT 0,
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(service_desk_id, synced_at)
);

-- Cleanup recommendations
CREATE TABLE IF NOT EXISTS cleanup_recommendations (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category     TEXT NOT NULL,
    item_name    TEXT NOT NULL,
    item_id      TEXT NOT NULL,
    reason       TEXT NOT NULL,
    impact       TEXT NOT NULL DEFAULT 'low',
    product      TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'open',  -- open | dismissed | resolved
    synced_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Permissions audit log
CREATE TABLE IF NOT EXISTS permissions_audit (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_type   TEXT NOT NULL,
    entity_name   TEXT NOT NULL,
    product       TEXT NOT NULL,
    scope         TEXT NOT NULL,
    scope_key     TEXT,
    permissions   JSONB NOT NULL DEFAULT '[]',
    synced_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- License usage snapshots
CREATE TABLE IF NOT EXISTS license_usage (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product         TEXT NOT NULL,
    total_licenses  INTEGER,
    active_users    INTEGER NOT NULL DEFAULT 0,
    inactive_users  INTEGER NOT NULL DEFAULT 0,
    synced_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Dashboard snapshots (for historical trending)
CREATE TABLE IF NOT EXISTS dashboard_snapshots (
    id                      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    jira_projects           INTEGER NOT NULL DEFAULT 0,
    confluence_spaces       INTEGER NOT NULL DEFAULT 0,
    jsm_service_desks       INTEGER NOT NULL DEFAULT 0,
    total_users             INTEGER NOT NULL DEFAULT 0,
    active_users            INTEGER NOT NULL DEFAULT 0,
    inactive_users          INTEGER NOT NULL DEFAULT 0,
    custom_fields_total     INTEGER NOT NULL DEFAULT 0,
    custom_fields_unused    INTEGER NOT NULL DEFAULT 0,
    cleanup_recommendations INTEGER NOT NULL DEFAULT 0,
    synced_at               TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_jira_users_account_id ON jira_users(account_id);
CREATE INDEX IF NOT EXISTS idx_jira_users_synced_at ON jira_users(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_custom_fields_synced_at ON custom_fields(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_jira_projects_synced_at ON jira_projects(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_confluence_spaces_synced_at ON confluence_spaces(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_jsm_service_desks_synced_at ON jsm_service_desks(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_cleanup_recs_status ON cleanup_recommendations(status);
CREATE INDEX IF NOT EXISTS idx_dashboard_snapshots_synced_at ON dashboard_snapshots(synced_at DESC);
CREATE INDEX IF NOT EXISTS idx_sync_history_category ON sync_history(category, synced_at DESC);

-- Enable Row Level Security (policies allow service-role full access by default)
ALTER TABLE sync_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE custom_fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE jira_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE schemes ENABLE ROW LEVEL SECURITY;
ALTER TABLE confluence_spaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE confluence_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE jsm_service_desks ENABLE ROW LEVEL SECURITY;
ALTER TABLE cleanup_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE permissions_audit ENABLE ROW LEVEL SECURITY;
ALTER TABLE license_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE dashboard_snapshots ENABLE ROW LEVEL SECURITY;

-- RLS policies: allow anon key read-only access for the dashboard frontend
CREATE POLICY "anon_read" ON sync_history FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_users FOR SELECT USING (true);
CREATE POLICY "anon_read" ON custom_fields FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jira_projects FOR SELECT USING (true);
CREATE POLICY "anon_read" ON workflows FOR SELECT USING (true);
CREATE POLICY "anon_read" ON schemes FOR SELECT USING (true);
CREATE POLICY "anon_read" ON confluence_spaces FOR SELECT USING (true);
CREATE POLICY "anon_read" ON confluence_content FOR SELECT USING (true);
CREATE POLICY "anon_read" ON jsm_service_desks FOR SELECT USING (true);
CREATE POLICY "anon_read" ON cleanup_recommendations FOR SELECT USING (true);
CREATE POLICY "anon_read" ON permissions_audit FOR SELECT USING (true);
CREATE POLICY "anon_read" ON license_usage FOR SELECT USING (true);
CREATE POLICY "anon_read" ON dashboard_snapshots FOR SELECT USING (true);
