import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { getRecentContent, getStaleContent, getTopContributors, getLabelUsage } from '../services/api'
import { MetricCard, Loading, ErrorBanner } from '../components/common/LoadingState'

export default function ConfluenceContentPage() {
  const [tab, setTab] = useState('recent')
  const { data: recent, loading: rL } = useApi(() => getRecentContent(30, 50))
  const { data: stale, loading: sL } = useApi(() => getStaleContent(365, 50))
  const { data: contributors, loading: cL } = useApi(() => getTopContributors(30, 20))
  const { data: labels, loading: lL } = useApi(getLabelUsage)

  if (rL || sL || cL || lL) return <Loading />

  return (
    <div>
      <div className="page-header">
        <h2>Content Analytics</h2>
        <p>Recent activity, stale content, contributors, and label usage</p>
      </div>

      <div className="metric-grid">
        <MetricCard label="Recent Updates (30d)" value={recent?.length || 0} color="green" />
        <MetricCard label="Stale Pages (1yr+)" value={stale?.length || 0} color="yellow" />
        <MetricCard label="Active Contributors" value={contributors?.length || 0} color="blue" />
        <MetricCard label="Labels in Use" value={labels?.length || 0} color="purple" />
      </div>

      <div className="tabs">
        {['recent', 'stale', 'contributors', 'labels'].map(t => (
          <button key={t} className={`tab ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {tab === 'recent' && (
        <div className="card">
          <table className="data-table">
            <thead><tr><th>Title</th><th>Space</th><th>Type</th><th>Version</th></tr></thead>
            <tbody>
              {(recent || []).map(c => (
                <tr key={c.content_id}>
                  <td>{c.title}</td>
                  <td><span className="badge green">{c.space_key}</span></td>
                  <td>{c.content_type}</td>
                  <td>{c.version}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'stale' && (
        <div className="card">
          <table className="data-table">
            <thead><tr><th>Title</th><th>Space</th><th>Version</th></tr></thead>
            <tbody>
              {(stale || []).map(c => (
                <tr key={c.content_id}>
                  <td>{c.title}</td>
                  <td><span className="badge yellow">{c.space_key}</span></td>
                  <td>{c.version}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'contributors' && (
        <div className="card">
          <table className="data-table">
            <thead><tr><th>Contributor</th><th>Edits (30d)</th></tr></thead>
            <tbody>
              {(contributors || []).map((c, i) => (
                <tr key={i}>
                  <td>{c.user}</td>
                  <td><span className="badge blue">{c.edits}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'labels' && (
        <div className="card">
          <table className="data-table">
            <thead><tr><th>Label</th><th>Pages Using</th></tr></thead>
            <tbody>
              {(labels || []).map((l, i) => (
                <tr key={i}>
                  <td><span className="badge purple">{l.label}</span></td>
                  <td>{l.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
