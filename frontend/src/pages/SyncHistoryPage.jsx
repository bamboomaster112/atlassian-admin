import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { getSyncHistory, triggerFullSync } from '../services/api'
import { Loading, ErrorBanner } from '../components/common/LoadingState'

const statusColor = { success: 'green', error: 'red' }

export default function SyncHistoryPage() {
  const { data, loading, error, reload } = useApi(() => getSyncHistory(100))
  const [syncing, setSyncing] = useState(false)

  const handleSync = async () => {
    setSyncing(true)
    try {
      await triggerFullSync()
      reload()
    } finally {
      setSyncing(false)
    }
  }

  if (loading) return <Loading />
  if (error) return <ErrorBanner message={error} />

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>Sync History</h2>
          <p>View past data sync operations and trigger new syncs</p>
        </div>
        <button
          onClick={handleSync}
          disabled={syncing}
          style={{
            background: 'var(--accent-blue)', color: '#fff', border: 'none',
            padding: '8px 20px', borderRadius: 6, fontSize: 13, cursor: 'pointer',
            opacity: syncing ? 0.6 : 1,
          }}
        >
          {syncing ? 'Syncing...' : 'Run Full Sync'}
        </button>
      </div>

      <div className="card">
        <table className="data-table">
          <thead>
            <tr>
              <th>Category</th>
              <th>Status</th>
              <th>Records</th>
              <th>Time</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            {(data || []).map((row, i) => (
              <tr key={i}>
                <td><span className="badge blue">{row.category}</span></td>
                <td><span className={`badge ${statusColor[row.status] || 'yellow'}`}>{row.status}</span></td>
                <td>{row.record_count}</td>
                <td style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                  {new Date(row.synced_at).toLocaleString()}
                </td>
                <td style={{ fontSize: 12, color: 'var(--accent-red)' }}>
                  {row.error_message || '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
