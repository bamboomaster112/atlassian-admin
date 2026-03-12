import { useApi } from '../hooks/useApi'
import { getDashboard } from '../services/api'
import { MetricCard, Loading, ErrorBanner } from '../components/common/LoadingState'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts'

const COLORS = ['#58a6ff', '#3fb950', '#d29922', '#f85149', '#bc8cff']

export default function DashboardPage() {
  const { data, loading, error } = useApi(getDashboard)

  if (loading) return <Loading />
  if (error) return <ErrorBanner message={error} />

  const productData = [
    { name: 'Jira Projects', value: data.jira_projects },
    { name: 'Confluence Spaces', value: data.confluence_spaces },
    { name: 'JSM Desks', value: data.jsm_service_desks },
  ]

  const userPie = [
    { name: 'Active', value: data.active_users },
    { name: 'Inactive', value: data.inactive_users },
  ]

  return (
    <div>
      <div className="page-header">
        <h2>Admin Dashboard</h2>
        <p>Cross-product overview of your Atlassian Cloud instance</p>
      </div>

      <div className="metric-grid">
        <MetricCard label="Jira Projects" value={data.jira_projects} color="blue" />
        <MetricCard label="Confluence Spaces" value={data.confluence_spaces} color="green" />
        <MetricCard label="JSM Service Desks" value={data.jsm_service_desks} color="purple" />
        <MetricCard label="Total Users" value={data.total_users} color="blue" />
        <MetricCard label="Active Users" value={data.active_users} color="green" />
        <MetricCard label="Inactive Users" value={data.inactive_users} color="yellow" />
        <MetricCard label="Custom Fields" value={data.custom_fields_total} color="blue" />
        <MetricCard label="Unused Custom Fields" value={data.custom_fields_unused} color="red" />
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
              <Tooltip contentStyle={{ background: '#1c2128', border: '1px solid #30363d', borderRadius: 8 }} />
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
              <Tooltip contentStyle={{ background: '#1c2128', border: '1px solid #30363d', borderRadius: 8 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
