import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import {
  getJiraProjects, getSchemes, getConfluenceSpaces,
  getSpaceGrowthSummary, getJSMOverview, getCustomFields
} from '../services/api'
import { MetricCard, Loading, ErrorBanner } from '../components/common/LoadingState'
import { ChevronDown, ChevronRight, FolderKanban, Globe, Headphones, Columns3, Shield, Bell, FileType } from 'lucide-react'

function Collapsible({ title, icon: Icon, count, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="card" style={{ marginBottom: 8 }}>
      <div
        className="card-header"
        style={{ cursor: 'pointer', userSelect: 'none' }}
        onClick={() => setOpen(!open)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {open ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          {Icon && <Icon size={16} style={{ color: 'var(--accent-blue)' }} />}
          <span className="card-title">{title}</span>
          {count !== undefined && (
            <span className="badge blue" style={{ marginLeft: 8 }}>{count}</span>
          )}
        </div>
      </div>
      {open && <div style={{ paddingTop: 8 }}>{children}</div>}
    </div>
  )
}

function SchemeSection({ title, icon: Icon, items }) {
  if (!items?.length) return null
  return (
    <Collapsible title={title} icon={Icon} count={items.length}>
      <table className="data-table">
        <thead>
          <tr><th>Name</th><th>ID</th><th>Default</th></tr>
        </thead>
        <tbody>
          {items.map((s, i) => (
            <tr key={i}>
              <td>{s.scheme_name || s.workflow_name}</td>
              <td style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{s.scheme_id || '—'}</td>
              <td>{s.is_default ? <span className="badge green">Default</span> : '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Collapsible>
  )
}

export default function InstanceOverviewPage() {
  const { data: projects, loading: pL } = useApi(getJiraProjects)
  const { data: schemes, loading: sL } = useApi(getSchemes)
  const { data: spaceSummary, loading: cL } = useApi(getSpaceGrowthSummary)
  const { data: jsmOverview, loading: jL } = useApi(getJSMOverview)
  const { data: customFields, loading: cfL } = useApi(getCustomFields)

  if (pL || sL || cL || jL || cfL) return <Loading />

  const byType = {}
  projects?.forEach(p => { byType[p.project_type] = (byType[p.project_type] || 0) + 1 })

  return (
    <div>
      <div className="page-header">
        <h2>Instance Overview</h2>
        <p>Hierarchical view of your Atlassian instance — Spaces, Schemes, and Configurations</p>
      </div>

      <div className="metric-grid">
        <MetricCard label="Jira Projects" value={projects?.length || 0} color="blue" />
        <MetricCard label="Confluence Spaces" value={spaceSummary?.total_spaces || 0} color="green" />
        <MetricCard label="JSM Desks" value={jsmOverview?.total_service_desks || 0} color="purple" />
        <MetricCard label="Custom Fields" value={customFields?.length || 0} color="yellow" />
      </div>

      {/* ── Level 1: Products ── */}

      <Collapsible title="Jira Projects" icon={FolderKanban} count={projects?.length} defaultOpen>
        {/* Level 2: Projects grouped by type */}
        {Object.entries(byType).map(([type, count]) => (
          <Collapsible key={type} title={`${type} (${count})`} count={count}>
            <table className="data-table">
              <thead><tr><th>Key</th><th>Name</th><th>Lead</th></tr></thead>
              <tbody>
                {projects?.filter(p => p.project_type === type).map(p => (
                  <tr key={p.project_key}>
                    <td><span className="badge blue">{p.project_key}</span></td>
                    <td>{p.project_name}</td>
                    <td>{p.lead || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Collapsible>
        ))}

        {/* Level 2: Schemes */}
        <div style={{ marginTop: 8, paddingLeft: 16, borderLeft: '2px solid var(--border)' }}>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8, fontWeight: 600 }}>
            Associated Schemes
          </div>
          <SchemeSection title="Workflows" icon={FolderKanban} items={schemes?.workflows?.items} />
          <SchemeSection title="Workflow Schemes" icon={FolderKanban} items={schemes?.workflow_schemes?.items} />
          <SchemeSection title="Permission Schemes" icon={Shield} items={schemes?.permission_schemes?.items} />
          <SchemeSection title="Notification Schemes" icon={Bell} items={schemes?.notification_schemes?.items} />
          <SchemeSection title="Issue Type Schemes" icon={FileType} items={schemes?.issue_type_schemes?.items} />
        </div>

        {/* Level 2: Custom Fields */}
        <div style={{ marginTop: 8, paddingLeft: 16, borderLeft: '2px solid var(--border)' }}>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8, fontWeight: 600 }}>
            Configurations
          </div>
          <Collapsible title="Custom Fields" icon={Columns3} count={customFields?.length}>
            <table className="data-table">
              <thead><tr><th>Name</th><th>Type</th><th>ID</th></tr></thead>
              <tbody>
                {customFields?.map(f => (
                  <tr key={f.field_id}>
                    <td>{f.field_name}</td>
                    <td><span className="badge blue">{f.field_type}</span></td>
                    <td style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{f.field_id}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Collapsible>
        </div>
      </Collapsible>

      <Collapsible title="Confluence Spaces" icon={Globe} count={spaceSummary?.total_spaces}>
        <div style={{ marginBottom: 12 }}>
          <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
            {spaceSummary?.total_pages || 0} pages · {spaceSummary?.total_blog_posts || 0} blog posts
          </span>
        </div>
        <table className="data-table">
          <thead><tr><th>Key</th><th>Name</th><th>Type</th><th>Pages</th><th>Blogs</th></tr></thead>
          <tbody>
            {(spaceSummary?.spaces || []).map(s => (
              <tr key={s.space_key}>
                <td><span className="badge green">{s.space_key}</span></td>
                <td>{s.space_name}</td>
                <td>{s.space_type}</td>
                <td>{s.total_pages}</td>
                <td>{s.total_blog_posts}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Collapsible>

      <Collapsible title="Jira Service Management" icon={Headphones} count={jsmOverview?.total_service_desks}>
        <div className="metric-grid" style={{ marginBottom: 12 }}>
          <MetricCard label="Request Types" value={jsmOverview?.total_request_types || 0} color="blue" />
          <MetricCard label="Queues" value={jsmOverview?.total_queues || 0} color="green" />
          <MetricCard label="Customers" value={jsmOverview?.total_customers || 0} color="yellow" />
        </div>
        <table className="data-table">
          <thead><tr><th>Name</th><th>Project</th><th>Req Types</th><th>Queues</th><th>Customers</th></tr></thead>
          <tbody>
            {(jsmOverview?.service_desks || []).map(d => (
              <tr key={d.service_desk_id}>
                <td>{d.service_desk_name}</td>
                <td><span className="badge purple">{d.project_key}</span></td>
                <td>{d.request_types}</td>
                <td>{d.queues}</td>
                <td>{d.customers}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Collapsible>
    </div>
  )
}
