import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Users, Columns3, Globe, ShieldCheck, RefreshCw, Network,
  FolderKanban, FileText, Headphones, Trash2, KeyRound, CreditCard,
  UsersRound, Filter, ScrollText,
} from 'lucide-react'

const sections = [
  {
    title: 'Overview',
    links: [
      { to: '/', label: 'Dashboard', icon: LayoutDashboard },
      { to: '/instance', label: 'Instance Overview', icon: Network },
      { to: '/sync', label: 'Sync History', icon: RefreshCw },
    ],
  },
  {
    title: 'Jira',
    links: [
      { to: '/jira/users', label: 'User Activity', icon: Users },
      { to: '/jira/custom-fields', label: 'Custom Fields', icon: Columns3 },
      { to: '/jira/schemes', label: 'Workflows & Schemes', icon: FolderKanban },
      { to: '/jira/projects', label: 'Projects', icon: FolderKanban },
      { to: '/jira/groups', label: 'Groups', icon: UsersRound },
      { to: '/jira/filters-dashboards', label: 'Filters & Dashboards', icon: Filter },
      { to: '/jira/audit-log', label: 'Audit Log', icon: ScrollText },
    ],
  },
  {
    title: 'Confluence',
    links: [
      { to: '/confluence/spaces', label: 'Spaces', icon: Globe },
      { to: '/confluence/content', label: 'Content Analytics', icon: FileText },
    ],
  },
  {
    title: 'Service Management',
    links: [
      { to: '/jsm/overview', label: 'JSM Overview', icon: Headphones },
    ],
  },
  {
    title: 'Governance',
    links: [
      { to: '/governance/licenses', label: 'Licenses', icon: CreditCard },
      { to: '/governance/permissions', label: 'Permissions Audit', icon: KeyRound },
      { to: '/governance/cleanup', label: 'Cleanup', icon: Trash2 },
    ],
  },
]

export default function Sidebar() {
  return (
    <nav className="sidebar">
      <div className="sidebar-header">
        <h1>Atlassian Admin</h1>
        <p>Governance & Tracking</p>
      </div>
      {sections.map((section) => (
        <div key={section.title} className="sidebar-section">
          <div className="sidebar-section-title">{section.title}</div>
          {section.links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === '/'}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? 'active' : ''}`
              }
            >
              <link.icon size={16} />
              {link.label}
            </NavLink>
          ))}
        </div>
      ))}
    </nav>
  )
}
