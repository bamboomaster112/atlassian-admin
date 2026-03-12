export function Loading() {
  return <div className="loading">Loading...</div>
}

export function ErrorBanner({ message }) {
  return <div className="error-banner">{message}</div>
}

export function MetricCard({ label, value, color = 'blue' }) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className={`metric-value ${color}`}>{value}</div>
    </div>
  )
}
