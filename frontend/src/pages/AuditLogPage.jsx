import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { getAuditLog, getInstanceInfo } from '../services/api'
import { MetricCard, Loading } from '../components/common/LoadingState'

export default function AuditLogPage() {
  const [limit, setLimit] = useState(100)
  const { data: entries, loading } = useApi(() => getAuditLog(limit), [limit])
  const { data: instanceInfo } = useApi(getInstanceInfo)

  if (loading) return <Loading />

  const categories = {}
  ;(entries || []).forEach(e => {
    const cat = e.category || 'unknown'
    categories[cat] = (categories[cat] || 0) + 1
  })

  return (
    <div>
      <div className="page-header">
        <h2>Audit Log</h2>
        <p>Recent administration changes tracked by Jira</p>
        {instanceInfo && (
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
            Instance: {instanceInfo.server_title} · v{instanceInfo.version}
          </div>
        )}
      </div>

      <div className="metric-grid">
        <MetricCard label="Entries Shown" value={entries?.length || 0} color="blue" />
        <MetricCard label="Categories" value={Object.keys(categories).length} color="green" />
      </div>

      <div style={{ marginBottom: 12, display: 'flex', gap: 8, alignItems: 'center' }}>
        <label style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Show last:</label>
        {[50, 100, 200, 500].map(n => (
          <button
            key={n}
            onClick={() => setLimit(n)}
            style={{
              padding: '4px 12px', borderRadius: 4, fontSize: 12, cursor: 'pointer',
              background: limit === n ? 'var(--accent-blue)' : 'var(--bg-tertiary)',
              color: limit === n ? '#fff' : 'var(--text-primary)',
              border: 'none',
            }}
          >{n}</button>
        ))}
      </div>

      <div className="card">
        <table className="data-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Summary</th>
              <th>Category</th>
              <th>Author</th>
              <th>Object</th>
              <th>Changes</th>
            </tr>
          </thead>
          <tbody>
            {(entries || []).map((e, i) => (
              <tr key={i}>
                <td style={{ fontSize: 11, whiteSpace: 'nowrap', color: 'var(--text-secondary)' }}>
                  {e.created ? new Date(e.created).toLocaleString() : '—'}
                </td>
                <td>{e.summary}</td>
                <td>{e.category ? <span className="badge blue">{e.category}</span> : '—'}</td>
                <td style={{ fontSize: 12 }}>{e.author_name || e.author_id || '—'}</td>
                <td style={{ fontSize: 12 }}>
                  {e.object_name ? `${e.object_type}: ${e.object_name}` : '—'}
                </td>
                <td style={{ fontSize: 11 }}>
                  {e.changed_values?.length > 0
                    ? e.changed_values.map((cv, j) => (
                        <div key={j} style={{ color: 'var(--text-secondary)' }}>
                          {cv.field_name}: {cv.changed_from || '(empty)'} → {cv.changed_to || '(empty)'}
                        </div>
                      ))
                    : '—'
                  }
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
