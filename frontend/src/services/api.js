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

// Jira
export const getJiraUsers = (activeOnly) => fetchJSON(`${BASE}/jira/users`, { active_only: activeOnly })
export const getUserActivitySummary = (days) => fetchJSON(`${BASE}/jira/users/activity-summary`, { days })
export const getUserActivity = (accountId, days) => fetchJSON(`${BASE}/jira/users/${accountId}/activity`, { days })
export const getInactiveUsers = (days) => fetchJSON(`${BASE}/jira/users/inactive`, { days })
export const getCustomFields = () => fetchJSON(`${BASE}/jira/custom-fields`)
export const getUnusedCustomFields = () => fetchJSON(`${BASE}/jira/custom-fields/unused`)
export const getCustomFieldUsage = (fieldId) => fetchJSON(`${BASE}/jira/custom-fields/${fieldId}/usage`)
export const getSchemes = () => fetchJSON(`${BASE}/jira/schemes`)
export const getJiraProjects = () => fetchJSON(`${BASE}/jira/projects`)
export const getProjectDetail = (key) => fetchJSON(`${BASE}/jira/projects/${key}`)

// Confluence
export const getConfluenceSpaces = () => fetchJSON(`${BASE}/confluence/spaces`)
export const getSpaceGrowthSummary = () => fetchJSON(`${BASE}/confluence/spaces/growth-summary`)
export const getSpaceDetail = (key) => fetchJSON(`${BASE}/confluence/spaces/${key}`)
export const getRecentContent = (days, limit) => fetchJSON(`${BASE}/confluence/content/recent`, { days, limit })
export const getStaleContent = (days, limit) => fetchJSON(`${BASE}/confluence/content/stale`, { days, limit })
export const getTopContributors = (days, limit) => fetchJSON(`${BASE}/confluence/content/top-contributors`, { days, limit })
export const getLabelUsage = () => fetchJSON(`${BASE}/confluence/content/labels`)

// JSM
export const getJSMOverview = () => fetchJSON(`${BASE}/jsm/overview`)
export const getServiceDesks = () => fetchJSON(`${BASE}/jsm/service-desks`)
export const getServiceDeskDetail = (id) => fetchJSON(`${BASE}/jsm/service-desks/${id}`)
export const getRequestTypes = (id) => fetchJSON(`${BASE}/jsm/service-desks/${id}/request-types`)
export const getQueues = (id) => fetchJSON(`${BASE}/jsm/service-desks/${id}/queues`)

// Governance
export const getLicenseSummary = () => fetchJSON(`${BASE}/governance/licenses`)
export const getPermissionsAudit = () => fetchJSON(`${BASE}/governance/permissions/audit`)
export const getCleanupRecommendations = () => fetchJSON(`${BASE}/governance/cleanup`)

// Sync
export const triggerFullSync = () => fetch(`${BASE}/sync/run`, { method: 'POST' }).then(r => r.json())
export const getSyncHistory = (limit) => fetchJSON(`${BASE}/sync/history`, { limit })

// Dashboard (Supabase-cached)
export const getDashboardCached = () => fetchJSON(`${BASE}/dashboard/cached`)
export const getDashboardTrends = (limit) => fetchJSON(`${BASE}/dashboard/trends`, { limit })
