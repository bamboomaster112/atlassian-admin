import { useApi } from '../hooks/useApi'
import { getSpaceGrowthSummary } from '../services/api'
import { MetricCard, Loading, ErrorBanner } from '../components/common/LoadingState'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function ConfluenceSpacesPage() {
  const { data, loading, error } = useApi(getSpaceGrowthSummary)

  if (loading) return <Loading />
  if (error) return <ErrorBanner message={error} />

  const chartData = (data.spaces || [])
    .sort((a, b) => b.total_pages - a.total_pages)
    .slice(0, 15)
    .map(s => ({ name: s.space_key, pages: s.total_pages, blogs: s.total_blog_posts }))

  return (
    <div>
      <div className="page-header">
        <h2>Confluence Spaces</h2>
        <p>Space usage, page counts, and growth overview</p>
      </div>

      <div className="metric-grid">
        <MetricCard label="Total Spaces" value={data.total_spaces} color="blue" />
        <MetricCard label="Total Pages" value={data.total_pages} color="green" />
        <MetricCard label="Total Blog Posts" value={data.total_blog_posts} color="purple" />
      </div>

      {chartData.length > 0 && (
        <div className="card">
          <div className="card-header"><span className="card-title">Top Spaces by Page Count</span></div>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
              <XAxis dataKey="name" stroke="#8b949e" fontSize={11} />
              <YAxis stroke="#8b949e" fontSize={12} />
              <Tooltip contentStyle={{ background: '#1c2128', border: '1px solid #30363d', borderRadius: 8 }} />
              <Bar dataKey="pages" fill="#3fb950" radius={[4, 4, 0, 0]} name="Pages" />
              <Bar dataKey="blogs" fill="#bc8cff" radius={[4, 4, 0, 0]} name="Blogs" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="card">
        <div className="card-header"><span className="card-title">All Spaces</span></div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Key</th>
              <th>Name</th>
              <th>Type</th>
              <th>Pages</th>
              <th>Blog Posts</th>
            </tr>
          </thead>
          <tbody>
            {(data.spaces || []).map(s => (
              <tr key={s.space_key}>
                <td><span className="badge green">{s.space_key}</span></td>
                <td>{s.space_name}</td>
                <td>{s.space_type}</td>
                <td>{s.total_pages}</td>
                <td>{s.total_blog_posts}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
