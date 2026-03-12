import { useApi } from '../hooks/useApi'
import { getCleanupRecommendations } from '../services/api'
import { MetricCard, Loading, ErrorBanner } from '../components/common/LoadingState'

const impactColor = { low: 'green', medium: 'yellow', high: 'red' }

export default function CleanupPage() {
  const { data, loading, error } = useApi(getCleanupRecommendations)

  if (loading) return <Loading />
  if (error) return <ErrorBanner message={error} />

  return (
    <div>
      <div className="page-header">
        <h2>Cleanup Recommendations</h2>
        <p>Actionable suggestions to reduce clutter and improve governance</p>
      </div>

      <div className="metric-grid">
        <MetricCard label="Total Recommendations" value={data.total_recommendations} color="yellow" />
        <MetricCard label="Low Impact" value={data.by_impact?.low || 0} color="green" />
        <MetricCard label="Medium Impact" value={data.by_impact?.medium || 0} color="yellow" />
        <MetricCard label="High Impact" value={data.by_impact?.high || 0} color="red" />
      </div>

      <div className="card">
        <table className="data-table">
          <thead>
            <tr>
              <th>Category</th>
              <th>Item</th>
              <th>Product</th>
              <th>Reason</th>
              <th>Impact</th>
            </tr>
          </thead>
          <tbody>
            {(data.recommendations || []).map((r, i) => (
              <tr key={i}>
                <td><span className="badge blue">{r.category}</span></td>
                <td>{r.item_name}</td>
                <td><span className="badge purple">{r.product}</span></td>
                <td style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{r.reason}</td>
                <td><span className={`badge ${impactColor[r.impact]}`}>{r.impact}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
