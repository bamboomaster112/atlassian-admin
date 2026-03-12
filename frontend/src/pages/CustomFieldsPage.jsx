import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { getCustomFields, getUnusedCustomFields } from '../services/api'
import { MetricCard, Loading, ErrorBanner } from '../components/common/LoadingState'

export default function CustomFieldsPage() {
  const [tab, setTab] = useState('all')
  const { data: allFields, loading: aLoading, error: aError } = useApi(getCustomFields)
  const { data: unused, loading: uLoading, error: uError } = useApi(getUnusedCustomFields)

  if (aLoading || uLoading) return <Loading />
  if (aError) return <ErrorBanner message={aError} />

  const fields = tab === 'unused' ? (unused || []) : (allFields || [])

  return (
    <div>
      <div className="page-header">
        <h2>Custom Fields</h2>
        <p>Audit custom field usage and identify candidates for cleanup</p>
      </div>

      <div className="metric-grid">
        <MetricCard label="Total Custom Fields" value={allFields?.length || 0} color="blue" />
        <MetricCard label="Unused Fields" value={unused?.length || 0} color="red" />
        <MetricCard label="Active Fields" value={(allFields?.length || 0) - (unused?.length || 0)} color="green" />
      </div>

      <div className="tabs">
        <button className={`tab ${tab === 'all' ? 'active' : ''}`} onClick={() => setTab('all')}>All Fields</button>
        <button className={`tab ${tab === 'unused' ? 'active' : ''}`} onClick={() => setTab('unused')}>Unused Fields</button>
      </div>

      <div className="card">
        <table className="data-table">
          <thead>
            <tr>
              <th>Field Name</th>
              <th>Type</th>
              <th>Field ID</th>
              {tab === 'unused' && <th>Recommendation</th>}
            </tr>
          </thead>
          <tbody>
            {fields.map(f => (
              <tr key={f.field_id}>
                <td>{f.field_name}</td>
                <td><span className="badge blue">{f.field_type}</span></td>
                <td style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{f.field_id}</td>
                {tab === 'unused' && <td><span className="badge yellow">{f.recommendation || 'Review'}</span></td>}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
