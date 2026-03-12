import { useApi } from '../hooks/useApi'
import { getJiraProjects } from '../services/api'
import { MetricCard, Loading, ErrorBanner } from '../components/common/LoadingState'

export default function JiraProjectsPage() {
  const { data, loading, error } = useApi(getJiraProjects)

  if (loading) return <Loading />
  if (error) return <ErrorBanner message={error} />

  const byType = {}
  data?.forEach(p => { byType[p.project_type] = (byType[p.project_type] || 0) + 1 })

  return (
    <div>
      <div className="page-header">
        <h2>Jira Projects</h2>
        <p>All projects in your instance</p>
      </div>

      <div className="metric-grid">
        <MetricCard label="Total Projects" value={data?.length || 0} color="blue" />
        {Object.entries(byType).map(([type, count]) => (
          <MetricCard key={type} label={type} value={count} color="green" />
        ))}
      </div>

      <div className="card">
        <table className="data-table">
          <thead>
            <tr>
              <th>Key</th>
              <th>Name</th>
              <th>Type</th>
              <th>Lead</th>
            </tr>
          </thead>
          <tbody>
            {data?.map(p => (
              <tr key={p.project_key}>
                <td><span className="badge blue">{p.project_key}</span></td>
                <td>{p.project_name}</td>
                <td>{p.project_type}</td>
                <td>{p.lead || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
