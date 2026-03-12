import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { getDashboardCached, getDashboardTrends, triggerFullSync } from '../services/api'
import { MetricCard, Loading, ErrorBanner } from '../components/common/LoadingState'
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts'

const COLORS = ['#58a6ff', '#3fb950', '#d29922', '#f85149', '#bc8cff']
const tooltipStyle = { background: '#1c2128', border: '1px solid #30363d', borderRadius: 8 }

export default function DashboardPage() {
  const { data, loading, error, reload } = useApi(getDashboardCached)
  const { data: trends } = useApi(() => getDashboardTrends(30))
  const [syncing, setSyncing] = useState(false)
  const [syncResult, setSyncResult] = useState(null)

  const handleSync = async () => {
    setSyncing(true)
    setSyncResult(null)
    try {
      const result = await triggerFullSync()
      setSyncResult(result)
      reload()
    } catch (e) {
      setSyncResult({ status: 'error', error: e.message })
    } finally {
      setSyncing(false)
    }
  }

  if (loading) return <Loading />

  // Show a prompt if no snapshots exist yet
  if (error || !data || data.message) {
    return (
      <div>
        <div className="page-header">
          <h2>Admin Dashboard</h2>
          <p>Cross-product overview of your Atlassian Cloud instance</p>
        </div>
        <div className="card" style={{ textAlign: 'center', padding: 40 }}>
          <p style={{ marginBottom: 16, color: 'var(--text-secondary)' }}>
            {data?.message || 'No data yet. Run your first sync to populate the dashboard.'}
          </p>
          <button
            onClick={handleSync}
            disabled={syncing}
            style={{
              background: 'var(--accent-blue)', color: '#fff', border: 'none',
              padding: '10px 24px', borderRadius: 6, fontSize: 14, cursor: 'pointer',
              opacity: syncing ? 0.6 : 1,
            }}
          >
            {syncing ? 'Syncing...' : 'Run Full Sync'}
          </button>
          {syncResult && (
            <p style={{ marginTop: 12, fontSize: 13, color: syncResult.status === 'error' ? 'var(--accent-red)' : 'var(--accent-green)' }}>
              {syncResult.status === 'error' ? syncResult.error : 'Sync completed! Refreshing...'}
            </p>
          )}
        </div>
      </div>
    )
  }

  const productData = [
    { name: 'Jira Projects', value: data.jira_projects },
    { name: 'Confluence Spaces', value: data.confluence_spaces },
    { name: 'JSM Desks', value: data.jsm_service_desks },
  ]

  const userPie = [
    { name: 'Active', value: data.active_users },
    { name: 'Inactive', value: data.inactive_users },
  ]

  // Prepare trend data (reverse so oldest is first)
  const trendData = (trends || []).reverse().map(t => ({
    ...t,
    date: new Date(t.synced_at).toLocaleDateString(),
  }))

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>Admin Dashboard</h2>
          <p>Cross-product overview of your Atlassian Cloud instance</p>
          {data.synced_at && (
            <p style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 4 }}>
              Last synced: {new Date(data.synced_at).toLocaleString()}
            </p>
          )}
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
          {syncing ? 'Syncing...' : 'Sync Now'}
        </button>
      </div>

      {syncResult && (
        <div className={syncResult.status === 'error' ? 'error-banner' : 'card'} style={{ marginBottom: 16, padding: '8px 16px', fontSize: 13 }}>
          {syncResult.status === 'error' ? syncResult.error : 'Sync completed successfully.'}
        </div>
      )}

      <div className="metric-grid">
        <MetricCard label="Jira Projects" value={data.jira_projects} color="blue" />
        <MetricCard label="Confluence Spaces" value={data.confluence_spaces} color="green" />
        <MetricCard label="JSM Service Desks" value={data.jsm_service_desks} color="purple" />
        <MetricCard label="Total Users" value={data.total_users} color="blue" />
        <MetricCard label="Active Users" value={data.active_users} color="green" />
        <MetricCard label="Inactive Users" value={data.inactive_users} color="yellow" />
        <MetricCard label="Custom Fields" value={data.custom_fields_total} color="blue" />
        <MetricCard label="Unused Fields" value={data.custom_fields_unused} color="red" />
        <MetricCard label="Workflows" value={data.total_workflows} color="blue" />
        <MetricCard label="Schemes" value={data.total_schemes} color="green" />
        <MetricCard label="Groups" value={data.total_groups} color="purple" />
        <MetricCard label="Filters" value={data.total_filters} color="blue" />
        <MetricCard label="Dashboards" value={data.total_dashboards_jira} color="green" />
        <MetricCard label="Cleanup Items" value={data.cleanup_recommendations} color="yellow" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div className="card">
          <div className="card-header"><span className="card-title">Product Usage</span></div>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={productData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
              <XAxis dataKey="name" stroke="#8b949e" fontSize={12} />
              <YAxis stroke="#8b949e" fontSize={12} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="value" fill="#58a6ff" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-header"><span className="card-title">User Status</span></div>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={userPie} cx="50%" cy="50%" innerRadius={60} outerRadius={90} dataKey="value" label>
                {userPie.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {trendData.length > 1 && (
        <div className="card">
          <div className="card-header"><span className="card-title">User Trends Over Time</span></div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
              <XAxis dataKey="date" stroke="#8b949e" fontSize={11} />
              <YAxis stroke="#8b949e" fontSize={12} />
              <Tooltip contentStyle={tooltipStyle} />
              <Legend />
              <Line type="monotone" dataKey="active_users" stroke="#3fb950" name="Active Users" strokeWidth={2} />
              <Line type="monotone" dataKey="inactive_users" stroke="#d29922" name="Inactive Users" strokeWidth={2} />
              <Line type="monotone" dataKey="total_users" stroke="#58a6ff" name="Total Users" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
