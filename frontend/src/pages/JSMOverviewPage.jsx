import { useApi } from '../hooks/useApi'
import { getJSMOverview } from '../services/api'
import { MetricCard, Loading, ErrorBanner } from '../components/common/LoadingState'

export default function JSMOverviewPage() {
  const { data, loading, error } = useApi(getJSMOverview)

  if (loading) return <Loading />
  if (error) return <ErrorBanner message={error} />

  return (
    <div>
      <div className="page-header">
        <h2>Jira Service Management</h2>
        <p>Service desk overview — request types, queues, and customers</p>
      </div>

      <div className="metric-grid">
        <MetricCard label="Service Desks" value={data.total_service_desks} color="purple" />
        <MetricCard label="Request Types" value={data.total_request_types} color="blue" />
        <MetricCard label="Queues" value={data.total_queues} color="green" />
        <MetricCard label="Customers" value={data.total_customers} color="yellow" />
      </div>

      <div className="card">
        <div className="card-header"><span className="card-title">Service Desks</span></div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Project</th>
              <th>Request Types</th>
              <th>Queues</th>
              <th>Customers</th>
            </tr>
          </thead>
          <tbody>
            {(data.service_desks || []).map(d => (
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
      </div>
    </div>
  )
}
