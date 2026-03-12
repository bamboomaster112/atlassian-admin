import { useApi } from '../hooks/useApi'
import { getLicenseSummary } from '../services/api'
import { MetricCard, Loading, ErrorBanner } from '../components/common/LoadingState'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'

const COLORS = ['#3fb950', '#d29922']

export default function LicensesPage() {
  const { data, loading, error } = useApi(getLicenseSummary)

  if (loading) return <Loading />
  if (error) return <ErrorBanner message={error} />

  return (
    <div>
      <div className="page-header">
        <h2>License Usage</h2>
        <p>Track active and inactive licenses across products</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 }}>
        {(data || []).map(lic => {
          const pieData = [
            { name: 'Active', value: lic.active_users },
            { name: 'Inactive', value: lic.inactive_users },
          ]
          return (
            <div className="card" key={lic.product}>
              <div className="card-header"><span className="card-title">{lic.product.toUpperCase()}</span></div>
              <div className="metric-grid" style={{ marginBottom: 12 }}>
                <MetricCard label="Active" value={lic.active_users} color="green" />
                <MetricCard label="Inactive" value={lic.inactive_users} color="yellow" />
              </div>
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} dataKey="value" label>
                    {pieData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#1c2128', border: '1px solid #30363d', borderRadius: 8 }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )
        })}
      </div>
    </div>
  )
}
