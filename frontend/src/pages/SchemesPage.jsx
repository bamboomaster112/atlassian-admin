import { useApi } from '../hooks/useApi'
import { getSchemes } from '../services/api'
import { MetricCard, Loading, ErrorBanner } from '../components/common/LoadingState'

function SchemeTable({ title, items }) {
  if (!items?.length) return null
  return (
    <div className="card">
      <div className="card-header"><span className="card-title">{title} ({items.length})</span></div>
      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>ID</th>
          </tr>
        </thead>
        <tbody>
          {items.map((s, i) => (
            <tr key={i}>
              <td>{s.scheme_name || s.workflow_name}</td>
              <td><span className="badge blue">{s.scheme_type || 'workflow'}</span></td>
              <td style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{s.scheme_id || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function SchemesPage() {
  const { data, loading, error } = useApi(getSchemes)

  if (loading) return <Loading />
  if (error) return <ErrorBanner message={error} />

  return (
    <div>
      <div className="page-header">
        <h2>Workflows & Schemes</h2>
        <p>Overview of all workflows, permission schemes, notification schemes, and issue type schemes</p>
      </div>

      <div className="metric-grid">
        <MetricCard label="Workflows" value={data.workflows?.count || 0} color="blue" />
        <MetricCard label="Workflow Schemes" value={data.workflow_schemes?.count || 0} color="green" />
        <MetricCard label="Permission Schemes" value={data.permission_schemes?.count || 0} color="purple" />
        <MetricCard label="Notification Schemes" value={data.notification_schemes?.count || 0} color="yellow" />
        <MetricCard label="Issue Type Schemes" value={data.issue_type_schemes?.count || 0} color="blue" />
      </div>

      <SchemeTable title="Workflows" items={data.workflows?.items} />
      <SchemeTable title="Workflow Schemes" items={data.workflow_schemes?.items} />
      <SchemeTable title="Permission Schemes" items={data.permission_schemes?.items} />
      <SchemeTable title="Notification Schemes" items={data.notification_schemes?.items} />
      <SchemeTable title="Issue Type Schemes" items={data.issue_type_schemes?.items} />
    </div>
  )
}
