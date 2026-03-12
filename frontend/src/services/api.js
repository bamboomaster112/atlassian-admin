const BASE = '/api'

async function fetchJSON(path, params = {}) {
  const url = new URL(path, window.location.origin)
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null) url.searchParams.set(k, v)
  })
  const res = await fetch(url)
  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`)
  return res.json()
}

// Dashboard
export const getDashboard = () => fetchJSON(`${BASE}/dashboard/`)
export const getDashboardCached = () => fetchJSON(`${BASE}/dashboard/cached`)
export const getDashboardTrends = (limit) => fetchJSON(`${BASE}/dashboard/trends`, { limit })

// Sync
export const triggerFullSync = () => fetch(`${BASE}/sync/run`, { method: 'POST' }).then(r => r.json())
export const triggerBackgroundSync = () => fetch(`${BASE}/sync/run?background=true`, { method: 'POST' }).then(r => r.json())
export const getSyncStatus = () => fetchJSON(`${BASE}/sync/status`)
export const getSyncHistory = (limit) => fetchJSON(`${BASE}/sync/history`, { limit })

// ── Jira: Users ─────────────────────────────────────
export const getJiraUsers = (activeOnly) => fetchJSON(`${BASE}/jira/users`, { active_only: activeOnly })
export const getUserActivitySummary = (days) => fetchJSON(`${BASE}/jira/users/activity-summary`, { days })
export const getUserActivity = (accountId, days) => fetchJSON(`${BASE}/jira/users/${accountId}/activity`, { days })
export const getInactiveUsers = (days) => fetchJSON(`${BASE}/jira/users/inactive`, { days })

// ── Jira: Custom Fields ─────────────────────────────
export const getCustomFields = () => fetchJSON(`${BASE}/jira/custom-fields`)
export const getUnusedCustomFields = () => fetchJSON(`${BASE}/jira/custom-fields/unused`)
export const getCustomFieldUsage = (fieldId) => fetchJSON(`${BASE}/jira/custom-fields/${fieldId}/usage`)

// ── Jira: Projects ──────────────────────────────────
export const getJiraProjects = () => fetchJSON(`${BASE}/jira/projects`)
export const getProjectDetail = (key) => fetchJSON(`${BASE}/jira/projects/${key}`)

// ── Jira: Schemes & Workflows ───────────────────────
export const getSchemes = () => fetchJSON(`${BASE}/jira/schemes`)

// ── Jira: Configuration ─────────────────────────────
export const getFullConfiguration = () => fetchJSON(`${BASE}/jira/configuration`)
export const getIssueTypes = () => fetchJSON(`${BASE}/jira/issue-types`)
export const getStatuses = () => fetchJSON(`${BASE}/jira/statuses`)
export const getPriorities = () => fetchJSON(`${BASE}/jira/priorities`)
export const getResolutions = () => fetchJSON(`${BASE}/jira/resolutions`)
export const getScreens = () => fetchJSON(`${BASE}/jira/screens`)
export const getScreenSchemes = () => fetchJSON(`${BASE}/jira/screen-schemes`)
export const getIssueTypeScreenSchemes = () => fetchJSON(`${BASE}/jira/issue-type-screen-schemes`)
export const getFieldConfigurations = () => fetchJSON(`${BASE}/jira/field-configurations`)
export const getFieldConfigSchemes = () => fetchJSON(`${BASE}/jira/field-config-schemes`)
export const getProjectCategories = () => fetchJSON(`${BASE}/jira/project-categories`)
export const getProjectRoles = () => fetchJSON(`${BASE}/jira/project-roles`)

// ── Jira: Groups & App Roles ────────────────────────
export const getGroups = () => fetchJSON(`${BASE}/jira/groups`)
export const getGroupsWithMembers = () => fetchJSON(`${BASE}/jira/groups/with-members`)
export const getApplicationRoles = () => fetchJSON(`${BASE}/jira/application-roles`)

// ── Jira: Filters & Dashboards ──────────────────────
export const getFilters = () => fetchJSON(`${BASE}/jira/filters`)
export const getJiraDashboards = () => fetchJSON(`${BASE}/jira/dashboards`)
export const getFiltersDashboardsSummary = () => fetchJSON(`${BASE}/jira/filters-dashboards`)

// ── Jira: Audit & Instance ──────────────────────────
export const getAuditLog = (limit) => fetchJSON(`${BASE}/jira/audit-log`, { limit })
export const getInstanceInfo = () => fetchJSON(`${BASE}/jira/instance-info`)

// ── Confluence ──────────────────────────────────────
export const getConfluenceSpaces = () => fetchJSON(`${BASE}/confluence/spaces`)
export const getSpaceGrowthSummary = () => fetchJSON(`${BASE}/confluence/spaces/growth-summary`)
export const getSpaceDetail = (key) => fetchJSON(`${BASE}/confluence/spaces/${key}`)
export const getRecentContent = (days, limit) => fetchJSON(`${BASE}/confluence/content/recent`, { days, limit })
export const getStaleContent = (days, limit) => fetchJSON(`${BASE}/confluence/content/stale`, { days, limit })
export const getTopContributors = (days, limit) => fetchJSON(`${BASE}/confluence/content/top-contributors`, { days, limit })
export const getLabelUsage = () => fetchJSON(`${BASE}/confluence/content/labels`)
export const getConfluenceTemplates = () => fetchJSON(`${BASE}/confluence/templates`)

// ── JSM ─────────────────────────────────────────────
export const getJSMOverview = () => fetchJSON(`${BASE}/jsm/overview`)
export const getServiceDesks = () => fetchJSON(`${BASE}/jsm/service-desks`)
export const getServiceDeskDetail = (id) => fetchJSON(`${BASE}/jsm/service-desks/${id}`)
export const getRequestTypes = (id) => fetchJSON(`${BASE}/jsm/service-desks/${id}/request-types`)
export const getQueues = (id) => fetchJSON(`${BASE}/jsm/service-desks/${id}/queues`)
export const getJSMOrganizations = () => fetchJSON(`${BASE}/jsm/organizations`)

// ── Governance ──────────────────────────────────────
export const getLicenseSummary = () => fetchJSON(`${BASE}/governance/licenses`)
export const getPermissionsAudit = () => fetchJSON(`${BASE}/governance/permissions/audit`)
export const getCleanupRecommendations = () => fetchJSON(`${BASE}/governance/cleanup`)
