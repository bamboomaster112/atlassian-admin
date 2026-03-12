import { useApi } from '../hooks/useApi'
import { getPermissionsAudit } from '../services/api'
import { MetricCard, Loading, ErrorBanner } from '../components/common/LoadingState'

export default function PermissionsPage() {
  const { data, loading, error } = useApi(getPermissionsAudit)

  if (loading) return <Loading />
  if (error) return <ErrorBanner message={error} />

  return (
    <div>
      <div className="page-header">
        <h2>Permissions Audit</h2>
        <p>Cross-product permissions review for Jira and Confluence</p>
      </div>

      <div className="metric-grid">
        <MetricCard label="Total Entries" value={data.total_entries} color="blue" />
        <MetricCard label="Jira Global" value={data.jira_global_permissions?.length || 0} color="purple" />
        <MetricCard label="Jira Project" value={data.jira_project_permissions?.length || 0} color="green" />
        <MetricCard label="Confluence Space" value={data.confluence_space_permissions?.length || 0} color="yellow" />
      </div>

      {data.jira_global_permissions?.length > 0 && (
        <div className="card">
          <div className="card-header"><span className="card-title">Jira Global Permissions</span></div>
          <table className="data-table">
            <thead><tr><th>Permission</th><th>Scope</th></tr></thead>
            <tbody>
              {data.jira_global_permissions.map((p, i) => (
                <tr key={i}>
                  <td>{p.entity_name}</td>
                  <td><span className="badge purple">{p.scope}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data.jira_project_permissions?.length > 0 && (
        <div className="card">
          <div className="card-header"><span className="card-title">Jira Project Permissions</span></div>
          <table className="data-table">
            <thead><tr><th>Entity</th><th>Type</th><th>Project</th><th>Permission</th></tr></thead>
            <tbody>
              {data.jira_project_permissions.map((p, i) => (
                <tr key={i}>
                  <td>{p.entity_name}</td>
                  <td><span className="badge blue">{p.entity_type}</span></td>
                  <td><span className="badge green">{p.scope_key}</span></td>
                  <td>{p.permissions.join(', ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data.confluence_space_permissions?.length > 0 && (
        <div className="card">
          <div className="card-header"><span className="card-title">Confluence Space Permissions</span></div>
          <table className="data-table">
            <thead><tr><th>Entity</th><th>Type</th><th>Space</th><th>Operation</th></tr></thead>
            <tbody>
              {data.confluence_space_permissions.map((p, i) => (
                <tr key={i}>
                  <td>{p.entity_name}</td>
                  <td><span className="badge yellow">{p.entity_type}</span></td>
                  <td><span className="badge green">{p.scope_key}</span></td>
                  <td>{p.permissions.join(', ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
