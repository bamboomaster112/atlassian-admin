import { useApi } from '../hooks/useApi'
import { getFiltersDashboardsSummary } from '../services/api'
import { MetricCard, Loading } from '../components/common/LoadingState'

export default function FiltersDashboardsPage() {
  const { data, loading } = useApi(getFiltersDashboardsSummary)

  if (loading) return <Loading />

  const filters = data?.filters?.items || []
  const dashboards = data?.dashboards?.items || []

  return (
    <div>
      <div className="page-header">
        <h2>Filters & Dashboards</h2>
        <p>Saved filters and shared dashboards across the Jira instance</p>
      </div>

      <div className="metric-grid">
        <MetricCard label="Filters" value={filters.length} color="blue" />
        <MetricCard label="Dashboards" value={dashboards.length} color="green" />
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-header"><span className="card-title">Filters</span></div>
        <table className="data-table">
          <thead>
            <tr><th>Name</th><th>Owner</th><th>Favourites</th><th>Shared</th><th>JQL</th></tr>
          </thead>
          <tbody>
            {filters.map((f, i) => (
              <tr key={i}>
                <td>{f.name}</td>
                <td>{f.owner_display_name || '—'}</td>
                <td>{f.favourite_count}</td>
                <td>{f.share_permissions?.length > 0 ? <span className="badge green">{f.share_permissions.length}</span> : '—'}</td>
                <td style={{ fontSize: 11, fontFamily: 'monospace', color: 'var(--text-secondary)', maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {f.jql || '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <div className="card-header"><span className="card-title">Dashboards</span></div>
        <table className="data-table">
          <thead>
            <tr><th>Name</th><th>Owner</th><th>Gadgets</th><th>System</th><th>Shared</th></tr>
          </thead>
          <tbody>
            {dashboards.map((d, i) => (
              <tr key={i}>
                <td>{d.name}</td>
                <td>{d.owner_display_name || '—'}</td>
                <td>{d.gadgets?.length || 0}</td>
                <td>{d.is_system ? <span className="badge yellow">System</span> : '—'}</td>
                <td>{d.share_permissions?.length > 0 ? <span className="badge green">{d.share_permissions.length}</span> : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
