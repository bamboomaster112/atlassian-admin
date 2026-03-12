import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { getGroupsWithMembers, getApplicationRoles } from '../services/api'
import { MetricCard, Loading } from '../components/common/LoadingState'
import { ChevronDown, ChevronRight } from 'lucide-react'

function GroupCard({ group }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="card" style={{ marginBottom: 8 }}>
      <div
        className="card-header"
        style={{ cursor: 'pointer', userSelect: 'none' }}
        onClick={() => setOpen(!open)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          <span className="card-title">{group.group.name}</span>
          <span className="badge blue">{group.member_count} members</span>
        </div>
      </div>
      {open && group.members.length > 0 && (
        <table className="data-table" style={{ marginTop: 8 }}>
          <thead>
            <tr><th>Name</th><th>Email</th><th>Status</th></tr>
          </thead>
          <tbody>
            {group.members.map((m, i) => (
              <tr key={i}>
                <td>{m.display_name || m.account_id}</td>
                <td style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{m.email || '—'}</td>
                <td>{m.active ? <span className="badge green">Active</span> : <span className="badge yellow">Inactive</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default function GroupsPage() {
  const { data: groups, loading: gL } = useApi(getGroupsWithMembers)
  const { data: appRoles, loading: aL } = useApi(getApplicationRoles)

  if (gL || aL) return <Loading />

  const totalMembers = (groups || []).reduce((sum, g) => sum + g.member_count, 0)

  return (
    <div>
      <div className="page-header">
        <h2>Groups & Application Roles</h2>
        <p>Manage groups, memberships, and product access entitlements</p>
      </div>

      <div className="metric-grid">
        <MetricCard label="Groups" value={groups?.length || 0} color="blue" />
        <MetricCard label="Total Memberships" value={totalMembers} color="green" />
        <MetricCard label="App Roles" value={appRoles?.length || 0} color="purple" />
      </div>

      {appRoles?.length > 0 && (
        <div className="card" style={{ marginBottom: 16 }}>
          <div className="card-header"><span className="card-title">Application Roles</span></div>
          <table className="data-table">
            <thead><tr><th>Role</th><th>Users</th><th>Remaining Seats</th><th>Unlimited</th></tr></thead>
            <tbody>
              {appRoles.map((r, i) => (
                <tr key={i}>
                  <td>{r.name}</td>
                  <td>{r.user_count}</td>
                  <td>{r.remaining_seats ?? '—'}</td>
                  <td>{r.has_unlimited_seats ? <span className="badge green">Yes</span> : 'No'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <h3 style={{ marginBottom: 12 }}>Groups ({groups?.length || 0})</h3>
      {(groups || []).map((g, i) => <GroupCard key={i} group={g} />)}
    </div>
  )
}
