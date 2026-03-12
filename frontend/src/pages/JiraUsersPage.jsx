import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { getUserActivitySummary, getJiraUsers } from '../services/api'
import { MetricCard, Loading, ErrorBanner } from '../components/common/LoadingState'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'

export default function JiraUsersPage() {
  const [days, setDays] = useState(30)
  const { data: summary, loading: sLoading, error: sError } = useApi(() => getUserActivitySummary(days), [days])
  const { data: users, loading: uLoading, error: uError } = useApi(getJiraUsers)

  if (sLoading || uLoading) return <Loading />
  if (sError) return <ErrorBanner message={sError} />
  if (uError) return <ErrorBanner message={uError} />

  return (
    <div>
      <div className="page-header">
        <h2>Jira User Activity</h2>
        <p>Track user engagement and identify inactive accounts</p>
      </div>

      <div className="tabs">
        {[7, 30, 90].map(d => (
          <button key={d} className={`tab ${days === d ? 'active' : ''}`} onClick={() => setDays(d)}>
            Last {d} days
          </button>
        ))}
      </div>

      <div className="metric-grid">
        <MetricCard label="Total Users" value={summary.total_users} color="blue" />
        <MetricCard label="Active Users" value={summary.active_users} color="green" />
        <MetricCard label="Inactive Users" value={summary.inactive_users} color="yellow" />
        <MetricCard label="Issues Created" value={summary.issues_created_last_n_days} color="blue" />
      </div>

      {summary.top_creators?.length > 0 && (
        <div className="card">
          <div className="card-header"><span className="card-title">Top Issue Creators (Last {days} Days)</span></div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={summary.top_creators} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
              <XAxis type="number" stroke="#8b949e" fontSize={12} />
              <YAxis dataKey="user" type="category" stroke="#8b949e" fontSize={12} width={150} />
              <Tooltip contentStyle={{ background: '#1c2128', border: '1px solid #30363d', borderRadius: 8 }} />
              <Bar dataKey="count" fill="#58a6ff" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="card">
        <div className="card-header"><span className="card-title">All Users</span></div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {users?.map(u => (
              <tr key={u.account_id}>
                <td>{u.display_name}</td>
                <td>{u.email || '—'}</td>
                <td><span className={`badge ${u.active ? 'green' : 'red'}`}>{u.active ? 'Active' : 'Inactive'}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
