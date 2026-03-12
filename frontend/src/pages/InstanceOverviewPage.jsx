import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import {
  getJiraProjects, getSchemes, getConfluenceSpaces,
  getSpaceGrowthSummary, getJSMOverview, getCustomFields,
  getFullConfiguration, getGroups, getFiltersDashboardsSummary,
  getInstanceInfo,
} from '../services/api'
import { MetricCard, Loading } from '../components/common/LoadingState'
import {
  ChevronDown, ChevronRight, FolderKanban, Globe, Headphones, Columns3,
  Shield, Bell, FileType, Settings, Users, Filter, LayoutDashboard,
  Layers, CircleDot, AlertTriangle, CheckCircle, ScreenShare,
} from 'lucide-react'

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

function ConfigTable({ items, columns }) {
  if (!items?.length) return <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>No items found</p>
  return (
    <table className="data-table">
      <thead>
        <tr>{columns.map(c => <th key={c.key}>{c.label}</th>)}</tr>
      </thead>
      <tbody>
        {items.map((item, i) => (
          <tr key={i}>
            {columns.map(c => <td key={c.key}>{c.render ? c.render(item) : item[c.key] || '—'}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function SchemeSection({ title, icon: Icon, items }) {
  if (!items?.length) return null
  return (
    <Collapsible title={title} icon={Icon} count={items.length}>
      <ConfigTable
        items={items}
        columns={[
          { key: 'name', label: 'Name', render: i => i.scheme_name || i.workflow_name || i.name },
          { key: 'description', label: 'Description', render: i => (i.description || '—').substring(0, 80) },
          { key: 'id', label: 'ID', render: i => <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{i.scheme_id || i.workflow_id || '—'}</span> },
          { key: 'default', label: 'Default', render: i => i.is_default ? <span className="badge green">Default</span> : '—' },
        ]}
      />
    </Collapsible>
  )
}

export default function InstanceOverviewPage() {
  const { data: projects, loading: pL } = useApi(getJiraProjects)
  const { data: schemes, loading: sL } = useApi(getSchemes)
  const { data: spaceSummary, loading: cL } = useApi(getSpaceGrowthSummary)
  const { data: jsmOverview, loading: jL } = useApi(getJSMOverview)
  const { data: customFields, loading: cfL } = useApi(getCustomFields)
  const { data: config, loading: confL } = useApi(getFullConfiguration)
  const { data: groups, loading: gL } = useApi(getGroups)
  const { data: fdSummary, loading: fdL } = useApi(getFiltersDashboardsSummary)
  const { data: instanceInfo } = useApi(getInstanceInfo)

  if (pL || sL || cL || jL || cfL || confL || gL || fdL) return <Loading />

  const byType = {}
  projects?.forEach(p => { byType[p.project_type] = (byType[p.project_type] || 0) + 1 })

  return (
    <div>
      <div className="page-header">
        <h2>Instance Overview</h2>
        <p>Hierarchical view of your Atlassian instance — Products, Schemes, and Configurations</p>
        {instanceInfo && (
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
            {instanceInfo.server_title} · {instanceInfo.deployment_type} · v{instanceInfo.version}
          </div>
        )}
      </div>

      <div className="metric-grid">
        <MetricCard label="Jira Projects" value={projects?.length || 0} color="blue" />
        <MetricCard label="Confluence Spaces" value={spaceSummary?.total_spaces || 0} color="green" />
        <MetricCard label="JSM Desks" value={jsmOverview?.total_service_desks || 0} color="purple" />
        <MetricCard label="Custom Fields" value={customFields?.length || 0} color="yellow" />
        <MetricCard label="Groups" value={groups?.length || 0} color="blue" />
        <MetricCard label="Filters" value={fdSummary?.filters?.count || 0} color="green" />
      </div>

      {/* ═══════════════ JIRA ═══════════════ */}

      <Collapsible title="Jira" icon={FolderKanban} count={projects?.length} defaultOpen>

        {/* Projects grouped by type */}
        <Collapsible title="Projects" icon={FolderKanban} count={projects?.length} defaultOpen>
          {Object.entries(byType).map(([type, count]) => (
            <Collapsible key={type} title={`${type} (${count})`} count={count}>
              <ConfigTable
                items={projects?.filter(p => p.project_type === type)}
                columns={[
                  { key: 'project_key', label: 'Key', render: p => <span className="badge blue">{p.project_key}</span> },
                  { key: 'project_name', label: 'Name' },
                  { key: 'lead', label: 'Lead' },
                  { key: 'category_name', label: 'Category' },
                  { key: 'description', label: 'Description', render: p => (p.description || '—').substring(0, 60) },
                ]}
              />
            </Collapsible>
          ))}
        </Collapsible>

        {/* Schemes */}
        <div style={{ marginTop: 8, paddingLeft: 16, borderLeft: '2px solid var(--border)' }}>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8, fontWeight: 600 }}>
            Schemes
          </div>
          <SchemeSection title="Workflows" icon={FolderKanban} items={schemes?.workflows?.items} />
          <SchemeSection title="Workflow Schemes" icon={FolderKanban} items={schemes?.workflow_schemes?.items} />
          <SchemeSection title="Permission Schemes" icon={Shield} items={schemes?.permission_schemes?.items} />
          <SchemeSection title="Notification Schemes" icon={Bell} items={schemes?.notification_schemes?.items} />
          <SchemeSection title="Issue Type Schemes" icon={FileType} items={schemes?.issue_type_schemes?.items} />
        </div>

        {/* Configuration */}
        <div style={{ marginTop: 8, paddingLeft: 16, borderLeft: '2px solid var(--border)' }}>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8, fontWeight: 600 }}>
            Configuration
          </div>

          <Collapsible title="Issue Types" icon={Layers} count={config?.issue_types?.count}>
            <ConfigTable
              items={config?.issue_types?.items}
              columns={[
                { key: 'name', label: 'Name' },
                { key: 'description', label: 'Description', render: i => (i.description || '—').substring(0, 60) },
                { key: 'subtask', label: 'Sub-task', render: i => i.subtask ? <span className="badge yellow">Sub-task</span> : '—' },
                { key: 'hierarchy_level', label: 'Level' },
                { key: 'scope', label: 'Scope', render: i => <span style={{ fontSize: 12 }}>{i.scope}</span> },
              ]}
            />
          </Collapsible>

          <Collapsible title="Statuses" icon={CircleDot} count={config?.statuses?.count}>
            <ConfigTable
              items={config?.statuses?.items}
              columns={[
                { key: 'name', label: 'Name' },
                { key: 'status_category', label: 'Category', render: i => {
                  const colors = { new: 'blue', indeterminate: 'yellow', done: 'green' }
                  return <span className={`badge ${colors[i.status_category] || ''}`}>{i.status_category}</span>
                }},
                { key: 'scope', label: 'Scope', render: i => <span style={{ fontSize: 12 }}>{i.scope}</span> },
              ]}
            />
          </Collapsible>

          <Collapsible title="Priorities" icon={AlertTriangle} count={config?.priorities?.count}>
            <ConfigTable
              items={config?.priorities?.items}
              columns={[
                { key: 'name', label: 'Name' },
                { key: 'description', label: 'Description', render: i => (i.description || '—').substring(0, 60) },
                { key: 'is_default', label: 'Default', render: i => i.is_default ? <span className="badge green">Default</span> : '—' },
              ]}
            />
          </Collapsible>

          <Collapsible title="Resolutions" icon={CheckCircle} count={config?.resolutions?.count}>
            <ConfigTable
              items={config?.resolutions?.items}
              columns={[
                { key: 'name', label: 'Name' },
                { key: 'description', label: 'Description' },
                { key: 'is_default', label: 'Default', render: i => i.is_default ? <span className="badge green">Default</span> : '—' },
              ]}
            />
          </Collapsible>

          <Collapsible title="Screens" icon={ScreenShare} count={config?.screens?.count}>
            <ConfigTable
              items={config?.screens?.items}
              columns={[
                { key: 'name', label: 'Name' },
                { key: 'description', label: 'Description', render: i => (i.description || '—').substring(0, 60) },
                { key: 'tab_count', label: 'Tabs' },
                { key: 'scope', label: 'Scope', render: i => <span style={{ fontSize: 12 }}>{i.scope}</span> },
              ]}
            />
          </Collapsible>

          <Collapsible title="Screen Schemes" icon={ScreenShare} count={config?.screen_schemes?.count}>
            <ConfigTable
              items={config?.screen_schemes?.items}
              columns={[
                { key: 'name', label: 'Name' },
                { key: 'description', label: 'Description', render: i => (i.description || '—').substring(0, 60) },
              ]}
            />
          </Collapsible>

          <Collapsible title="Field Configurations" icon={Settings} count={config?.field_configurations?.count}>
            <ConfigTable
              items={config?.field_configurations?.items}
              columns={[
                { key: 'name', label: 'Name' },
                { key: 'description', label: 'Description', render: i => (i.description || '—').substring(0, 60) },
                { key: 'is_default', label: 'Default', render: i => i.is_default ? <span className="badge green">Default</span> : '—' },
              ]}
            />
          </Collapsible>

          <Collapsible title="Field Config Schemes" icon={Settings} count={config?.field_config_schemes?.count}>
            <ConfigTable
              items={config?.field_config_schemes?.items}
              columns={[
                { key: 'name', label: 'Name' },
                { key: 'description', label: 'Description', render: i => (i.description || '—').substring(0, 60) },
                { key: 'is_default', label: 'Default', render: i => i.is_default ? <span className="badge green">Default</span> : '—' },
              ]}
            />
          </Collapsible>

          <Collapsible title="Custom Fields" icon={Columns3} count={customFields?.length}>
            <ConfigTable
              items={customFields}
              columns={[
                { key: 'field_name', label: 'Name' },
                { key: 'field_type', label: 'Type', render: f => <span className="badge blue">{f.field_type}</span> },
                { key: 'field_id', label: 'ID', render: f => <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{f.field_id}</span> },
                { key: 'description', label: 'Description', render: f => (f.description || '—').substring(0, 50) },
              ]}
            />
          </Collapsible>

          <Collapsible title="Project Categories" icon={FolderKanban} count={config?.project_categories?.count}>
            <ConfigTable
              items={config?.project_categories?.items}
              columns={[
                { key: 'name', label: 'Name' },
                { key: 'description', label: 'Description' },
              ]}
            />
          </Collapsible>

          <Collapsible title="Project Roles" icon={Users} count={config?.project_roles?.count}>
            <ConfigTable
              items={config?.project_roles?.items}
              columns={[
                { key: 'name', label: 'Name' },
                { key: 'description', label: 'Description' },
              ]}
            />
          </Collapsible>
        </div>

        {/* Groups */}
        <div style={{ marginTop: 8, paddingLeft: 16, borderLeft: '2px solid var(--border)' }}>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8, fontWeight: 600 }}>
            Access & Permissions
          </div>
          <Collapsible title="Groups" icon={Users} count={groups?.length}>
            <ConfigTable
              items={groups}
              columns={[
                { key: 'name', label: 'Name' },
                { key: 'group_id', label: 'ID', render: g => <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{g.group_id}</span> },
              ]}
            />
          </Collapsible>
        </div>

        {/* Filters & Dashboards */}
        <div style={{ marginTop: 8, paddingLeft: 16, borderLeft: '2px solid var(--border)' }}>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8, fontWeight: 600 }}>
            Saved Artifacts
          </div>
          <Collapsible title="Filters" icon={Filter} count={fdSummary?.filters?.count}>
            <ConfigTable
              items={fdSummary?.filters?.items}
              columns={[
                { key: 'name', label: 'Name' },
                { key: 'owner_display_name', label: 'Owner' },
                { key: 'favourite_count', label: 'Favourites' },
                { key: 'jql', label: 'JQL', render: f => <span style={{ fontSize: 11, color: 'var(--text-secondary)', fontFamily: 'monospace' }}>{(f.jql || '—').substring(0, 60)}</span> },
              ]}
            />
          </Collapsible>

          <Collapsible title="Dashboards" icon={LayoutDashboard} count={fdSummary?.dashboards?.count}>
            <ConfigTable
              items={fdSummary?.dashboards?.items}
              columns={[
                { key: 'name', label: 'Name' },
                { key: 'owner_display_name', label: 'Owner' },
                { key: 'gadgets', label: 'Gadgets', render: d => d.gadgets?.length || 0 },
                { key: 'is_system', label: 'System', render: d => d.is_system ? <span className="badge yellow">System</span> : '—' },
              ]}
            />
          </Collapsible>
        </div>

      </Collapsible>

      {/* ═══════════════ CONFLUENCE ═══════════════ */}

      <Collapsible title="Confluence" icon={Globe} count={spaceSummary?.total_spaces}>
        <div style={{ marginBottom: 12 }}>
          <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
            {spaceSummary?.total_pages || 0} pages · {spaceSummary?.total_blog_posts || 0} blog posts
          </span>
        </div>
        <ConfigTable
          items={spaceSummary?.spaces}
          columns={[
            { key: 'space_key', label: 'Key', render: s => <span className="badge green">{s.space_key}</span> },
            { key: 'space_name', label: 'Name' },
            { key: 'space_type', label: 'Type' },
            { key: 'description', label: 'Description', render: s => (s.description || '—').substring(0, 50) },
            { key: 'total_pages', label: 'Pages' },
            { key: 'total_blog_posts', label: 'Blogs' },
          ]}
        />
      </Collapsible>

      {/* ═══════════════ JSM ═══════════════ */}

      <Collapsible title="Jira Service Management" icon={Headphones} count={jsmOverview?.total_service_desks}>
        <div className="metric-grid" style={{ marginBottom: 12 }}>
          <MetricCard label="Request Types" value={jsmOverview?.total_request_types || 0} color="blue" />
          <MetricCard label="Queues" value={jsmOverview?.total_queues || 0} color="green" />
          <MetricCard label="Customers" value={jsmOverview?.total_customers || 0} color="yellow" />
        </div>
        <ConfigTable
          items={jsmOverview?.service_desks}
          columns={[
            { key: 'service_desk_name', label: 'Name' },
            { key: 'project_key', label: 'Project', render: d => <span className="badge purple">{d.project_key}</span> },
            { key: 'request_types', label: 'Req Types' },
            { key: 'queues', label: 'Queues' },
            { key: 'customers', label: 'Customers' },
          ]}
        />
      </Collapsible>
    </div>
  )
}
